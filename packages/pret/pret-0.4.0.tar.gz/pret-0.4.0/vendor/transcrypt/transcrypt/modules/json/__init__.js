var __name__ = "json";


function __ensure_ascii(s) {
  return s.replace(/[\u007F-\uFFFF]/g,
    function(c) {
      var hex = c.charCodeAt(0).toString(16).padStart(4, "0");
      return "\\u" + hex;
    });
}

function __sort_keys(value) {
  if (Array.isArray(value)) {
    return value.map(__sort_keys);
  } else if (value !== null && typeof value === "object") {
    var out = {};
    Object.keys(value).sort().forEach(function(k) {
      out [k] = __sort_keys(value [k]);
    });
    return out;
  }
  return value;
}


export function dumps(obj /* …kwargs */) {

  var kwargs = arguments.length > 1 ? arguments [arguments.length - 1] : null;
  if (!kwargs || !kwargs.__kwargtrans__) {
    kwargs = {};
  }

  var indent = kwargs.indent ?? null;
  var sort_keys = kwargs.sort_keys ?? false;
  var ensure_ascii = kwargs.ensure_ascii ?? true;
  var default_fn = kwargs.default ?? null;
  var allow_nan = kwargs.allow_nan ?? true;


  function replacer(key, value) {

    var val = value;

    if (typeof val === "number") {
      if (!allow_nan && (!isFinite(val))) {
        throw __builtins__.ValueError("Out of range float values are not JSON compliant");
      }

    }
    if (val === undefined || typeof val === "function" || typeof val === "symbol") {

      return undefined;
    }
    if (val !== null && typeof val === "object") {
      return val;
    }
    return val;
  }


  var to_dump = sort_keys ? __sort_keys(obj) : obj;

  var jsonStr = JSON.stringify(
    to_dump,
    default_fn
      ? function(k, v) {

        try {
          return replacer(k, v);
        } catch (e) {
          throw e;
        }

      }
      : replacer,
    indent
  );

  if (ensure_ascii) {
    jsonStr = __ensure_ascii(jsonStr);
  }
  return jsonStr;
}


export function loads(s /* …kwargs */) {
  var kwargs = arguments.length > 1 ? arguments [arguments.length - 1] : null;
  if (!kwargs || !kwargs.__kwargtrans__) {
    kwargs = {};
  }

  var object_hook = kwargs.object_hook ?? null;
  var parse_float = kwargs.parse_float ?? null;
  var parse_int = kwargs.parse_int ?? null;
  var parse_constant = kwargs.parse_constant ?? null;


  function reviver(key, value) {
    if (typeof value === "string") {
      if (parse_constant && (value === "NaN" || value === "Infinity" || value === "-Infinity")) {
        return parse_constant(value);
      }
    }
    if (typeof value === "number") {
      if (!Number.isInteger(value) && parse_float) {
        return parse_float(String(value));
      } else if (Number.isInteger(value) && parse_int) {
        return parse_int(String(value));
      }
    }
    return value;
  }

  var result = JSON.parse(s, (parse_float || parse_int || parse_constant) ? reviver : undefined);

  if (object_hook && result !== null && typeof result === "object" && !Array.isArray(result)) {
    return object_hook(result);
  }
  return result;
}

