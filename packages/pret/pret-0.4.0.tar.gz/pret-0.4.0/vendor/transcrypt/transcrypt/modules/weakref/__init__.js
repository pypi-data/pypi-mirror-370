import {
  _class_,
  object,
  __get__,
  py_TypeError,
  py_KeyError
} from "./org.transcrypt.__runtime__.js";

var __name__ = "weakref";


export var ref = _class_("ref", [object], {
  __module__: __name__,

  get __init__() {
    return __get__(this, function(self, obj, callback) {
      // obj: the target object to reference weakly
      // callback: optional function to call with the ref instance when obj is GC’ed

      // Store a WeakRef to the target object
      self._ref = new WeakRef(obj);

      if (callback !== undefined && callback !== null) {
        // Capture `self` to use inside the FinalizationRegistry callback
        var _self = self;
        // Create a FinalizationRegistry that will invoke `callback(_self)`
        self._registry = new FinalizationRegistry(function(heldValue) {
          // heldValue is the ref instance (i.e., _self)
          try {
            // Invoke callback, passing the weakref instance
            callback(heldValue);
          } catch (err) {
            // Silently ignore exceptions in the user’s callback
          }
        });
        // Register the target object with the registry, holding `self` as token
        self._registry.register(obj, _self);
      }
    });
  },

  // __call__ returns the referenced object or null if it has been collected
  get __call__() {
    return __get__(this, function(self) {
      var deref = self._ref.deref();
      // In JavaScript, WeakRef.deref() returns `undefined` if collected
      return (deref === undefined ? null : deref);
    });
  },

  // Optionally, allow checking if the referent is still alive:
  get alive() {
    return __get__(this, function(self) {
      return (self._ref.deref() !== undefined);
    });
  }
});


export var WeakKeyDictionary = _class_("WeakKeyDictionary", [object], {
  __module__: __name__,

  get __init__() {
    return __get__(this, function(self) {
      // Underlying WeakMap holds keys weakly
      self._wm = new WeakMap();
    });
  },

  get __setitem__() {
    return __get__(this, function(self, key, value) {
      // Keys must be non-null objects
      if ((typeof key !== "object" && typeof key !== "function") || key === null) {
        throw py_TypeError("WeakKeyDictionary keys must be objects");
      }
      self._wm.set(key, value);
    });
  },

  get __getitem__() {
    return __get__(this, function(self, key) {
      var val = self._wm.get(key);
      if (val === undefined) {
        // If `undefined`, either key not present or stored value was actually `undefined`.
        // We assume no one stores literal `undefined` as a value; mimic Python KeyError.
        throw py_KeyError(key);
      }
      return val;
    });
  },

  get __delitem__() {
    return __get__(this, function(self, key) {
      var success = self._wm.delete(key);
      if (!success) {
        throw py_KeyError(key);
      }
    });
  },

  get __contains__() {
    return __get__(this, function(self, key) {
      return self._wm.has(key);
    });
  },

  // get(key, default=None)
  get get() {
    return __get__(this, function(self, key, defaultValue) {
      if (defaultValue === undefined) {
        defaultValue = null;  // Transcrypt maps None → null
      }
      var val = self._wm.get(key);
      return (val === undefined ? defaultValue : val);
    });
  },

  // pop(key, default=_marker): if key missing and default not given, raise KeyError
  get pop() {
    return __get__(this, function(self, key, defaultValue) {
      var has = self._wm.has(key);
      if (!has) {
        if (defaultValue === undefined) {
          throw py_KeyError(key);
        }
        return defaultValue;
      }
      var val = self._wm.get(key);
      self._wm.delete(key);
      return val;
    });
  },

  // Optional: clear all entries (not typical in a real WeakMap, but we can recreate it)
  get clear() {
    return __get__(this, function(self) {
      self._wm = new WeakMap();
    });
  }
});


export var WeakValueDictionary = _class_("WeakValueDictionary", [object], {
  __module__: __name__,

  get __init__() {
    return __get__(this, function(self) {
      // Underlying Map holds keys → WeakRef(value)
      self._map = new Map();

      // FinalizationRegistry will receive the key as “heldValue” when a value is GC’ed
      var _self = self;
      self._registry = new FinalizationRegistry(function(heldKey) {
        // Remove the entry for that key when its value is collected
        try {
          _self._map.delete(heldKey);
        } catch (err) {
          // Silently ignore if deletion fails
        }
      });
    });
  },

  get __setitem__() {
    return __get__(this, function(self, key, value) {
      // Create a WeakRef to the value
      var wref = new WeakRef(value);
      self._map.set(key, wref);
      // Register the value; when it’s GC’ed, callback gets “heldKey”
      self._registry.register(value, key);
    });
  },

  get __getitem__() {
    return __get__(this, function(self, key) {
      var wref = self._map.get(key);
      if (wref === undefined) {
        throw py_KeyError(key);
      }
      var val = wref.deref();
      if (val === undefined) {
        // Value was collected; remove stale entry and raise KeyError
        self._map.delete(key);
        throw py_KeyError(key);
      }
      return val;
    });
  },

  get __delitem__() {
    return __get__(this, function(self, key) {
      var existed = self._map.delete(key);
      if (!existed) {
        throw py_KeyError(key);
      }
    });
  },

  get __contains__() {
    return __get__(this, function(self, key) {
      var wref = self._map.get(key);
      if (wref === undefined) {
        return false;
      }
      var val = wref.deref();
      if (val === undefined) {
        // Stale entry; clean it up
        self._map.delete(key);
        return false;
      }
      return true;
    });
  },

  // get(key, default=None)
  get get() {
    return __get__(this, function(self, key, defaultValue) {
      if (defaultValue === undefined) {
        defaultValue = null;
      }
      var wref = self._map.get(key);
      if (wref === undefined) {
        return defaultValue;
      }
      var val = wref.deref();
      if (val === undefined) {
        self._map.delete(key);
        return defaultValue;
      }
      return val;
    });
  },

  // pop(key, default=_marker)
  get pop() {
    return __get__(this, function(self, key, defaultValue) {
      var wref = self._map.get(key);
      if (wref === undefined) {
        if (defaultValue === undefined) {
          throw py_KeyError(key);
        }
        return defaultValue;
      }
      var val = wref.deref();
      self._map.delete(key);
      if (val === undefined) {
        if (defaultValue === undefined) {
          throw py_KeyError(key);
        }
        return defaultValue;
      }
      return val;
    });
  },

  // items(): generator that yields [key, value] pairs for live values
  get items() {
    return __get__(this, function* (self) {
      for (var pair of self._map.entries()) {
        var key = pair[0];
        var wref = pair[1];
        var val = wref.deref();
        if (val === undefined) {
          // Clean up stale
          self._map.delete(key);
        } else {
          yield [key, val];
        }
      }
    });
  },

  // clear all entries
  get clear() {
    return __get__(this, function(self) {
      self._map = new Map();
    });
  }
});

