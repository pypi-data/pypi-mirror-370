use pyo3::prelude::*;
use pyo3::types::PyList;
use serde_json::Value;

/// Helper: check if a path matches rules
fn path_matches(path: &str, rules: &Vec<String>) -> bool {
    rules.iter().any(|rule| {
        // Direct match
        if path == rule {
            return true;
        }
        
        // Convert dot notation to slash notation for comparison
        let rule_slash = rule.replace('.', "/");
        if path == rule_slash {
            return true;
        }
        
        // Check if path ends with the rule (with slash)
        if path.ends_with(&format!("/{}", rule)) {
            return true;
        }
        
        // Check if path ends with the rule (with slash, converted from dot)
        if path.ends_with(&format!("/{}", rule_slash)) {
            return true;
        }
        
        // Check if the rule is a prefix of the path
        if path.starts_with(&format!("{}/", rule)) || path.starts_with(&format!("{}/", rule_slash)) {
            return true;
        }
        
        // Check if the path is a prefix of the rule (for parent paths)
        if rule.starts_with(&format!("{}/", path)) || rule_slash.starts_with(&format!("{}/", path)) {
            return true;
        }
        
        false
    })
}

/// Convert Python object to serde_json::Value
fn py_to_json(py: Python, obj: &Bound<'_, PyAny>) -> PyResult<Value> {
    if obj.is_none() {
        Ok(Value::Null)
    } else if let Ok(val) = obj.extract::<bool>() {
        Ok(Value::Bool(val))
    } else if let Ok(val) = obj.extract::<i64>() {
        Ok(Value::Number(serde_json::Number::from(val)))
    } else if let Ok(val) = obj.extract::<f64>() {
        if let Some(num) = serde_json::Number::from_f64(val) {
            Ok(Value::Number(num))
        } else {
            Ok(Value::Null)
        }
    } else if let Ok(val) = obj.extract::<String>() {
        Ok(Value::String(val))
    } else if let Ok(list) = obj.downcast::<PyList>() {
        let mut json_list = Vec::new();
        for item in list.iter() {
            json_list.push(py_to_json(py, &item)?);
        }
        Ok(Value::Array(json_list))
    } else if let Ok(dict) = obj.downcast::<pyo3::types::PyDict>() {
        let mut json_obj = serde_json::Map::new();
        for (key, value) in dict.iter() {
            let key_str = key.extract::<String>()?;
            let json_value = py_to_json(py, &value)?;
            json_obj.insert(key_str, json_value);
        }
        Ok(Value::Object(json_obj))
    } else {
        // Fallback: convert to string
        let repr = obj.repr()?.extract::<String>()?;
        Ok(Value::String(repr))
    }
}

fn compare_values(
    v1: &Value,
    v2: &Value,
    ignore: &Vec<String>,
    allow: &Vec<String>,
    path: &str,
    diffs: &mut Vec<String>,
) {
    // Path filtering
    if !allow.is_empty() && !path.is_empty() && !path_matches(path, allow) {
        return; // skip if not in allow list
    }
    if path_matches(path, ignore) {
        return; // skip if in ignore list
    }

    match (v1, v2) {
        (Value::Object(m1), Value::Object(m2)) => {
            for (k, val1) in m1 {
                let new_path = if path.is_empty() {
                    k.to_string()
                } else {
                    format!("{}/{}", path, k)
                };
                match m2.get(k) {
                    Some(val2) => compare_values(val1, val2, ignore, allow, &new_path, diffs),
                    None => diffs.push(format!("Missing key in second JSON: {}", new_path)),
                }
            }
            for k in m2.keys() {
                if !m1.contains_key(k) {
                    let new_path = if path.is_empty() {
                        k.to_string()
                    } else {
                        format!("{}/{}", path, k)
                    };
                    compare_values(&Value::Null, &m2[k], ignore, allow, &new_path, diffs);
                }
            }
        }
        _ => {
            if v1 != v2 {
                diffs.push(format!("Value mismatch at {}: {:?} vs {:?}", path, v1, v2));
            }
        }
    }
}

#[pyfunction]
#[pyo3(signature = (j1, j2, ignore=None, allow=None))]
/// Compare two JSON objects and return a list of differences.
///
/// This function performs a deep comparison of two JSON objects and returns
/// a list of strings describing the differences found. It supports path-based
/// filtering using `ignore` and `allow` parameters to control which parts
/// of the JSON are compared.
///
/// Args:
///     j1: The first JSON object to compare. Can be a dict, list, or any JSON-serializable object.
///     j2: The second JSON object to compare. Can be a dict, list, or any JSON-serializable object.
///     ignore: Optional list of paths to ignore during comparison. Paths can use either
///             dot notation (e.g., "args.field") or slash notation (e.g., "args/field").
///             If a path is in the ignore list, it and all its children will be skipped.
///     allow: Optional list of paths to include in comparison. If provided, only paths
///            that match the allow list (or are parent paths of allowed paths) will be compared.
///            Paths can use either dot notation (e.g., "args.field") or slash notation (e.g., "args/field").
///            If allow is empty or None, all paths are compared (except those in ignore).
///
/// Returns:
///     A list of strings describing the differences found. Each string describes
///     a specific difference, such as:
///     - "Value mismatch at path: value1 vs value2"
///     - "Missing key in second JSON: path"
///
/// Raises:
///     ValueError: If the input objects cannot be converted to JSON.
///
/// Examples:
///     >>> import fastjsondiff
///     >>> json1 = {"a": 1, "b": {"c": 2}}
///     >>> json2 = {"a": 1, "b": {"c": 3}}
///     >>> fastjsondiff.compare_json(json1, json2)
///     ['Value mismatch at b/c: Number(2) vs Number(3)']
///
///     >>> # Using ignore to skip certain paths
///     >>> fastjsondiff.compare_json(json1, json2, ignore=["b"])
///     []
///
///     >>> # Using allow to only compare specific paths
///     >>> fastjsondiff.compare_json(json1, json2, allow=["b/c"])
///     ['Value mismatch at b/c: Number(2) vs Number(3)']
///
///     >>> # Using dot notation for paths
///     >>> fastjsondiff.compare_json(json1, json2, allow=["b.c"])
///     ['Value mismatch at b/c: Number(2) vs Number(3)']
fn compare_json(
    py: Python,
    j1: &Bound<'_, PyAny>,
    j2: &Bound<'_, PyAny>,
    ignore: Option<&Bound<'_, PyList>>,
    allow: Option<&Bound<'_, PyList>>,
) -> PyResult<Vec<String>> {
    // Convert inputs into serde_json Values
    let j1_val = py_to_json(py, j1)?;
    let j2_val = py_to_json(py, j2)?;

    // Build ignore list
    let mut ignore_vec = Vec::new();
    if let Some(list) = ignore {
        for item in list.iter() {
            ignore_vec.push(item.extract::<String>()?);
        }
    }

    // Build allow list
    let mut allow_vec = Vec::new();
    if let Some(list) = allow {
        for item in list.iter() {
            allow_vec.push(item.extract::<String>()?);
        }
    }

    let mut diffs = Vec::new();
    compare_values(&j1_val, &j2_val, &ignore_vec, &allow_vec, "", &mut diffs);
    Ok(diffs)
}

#[pymodule]
/// Fast JSON difference detection library.
///
/// This module provides fast JSON comparison functionality with support for
/// path-based filtering. It's implemented in Rust for high performance and
/// provides a simple Python interface.
///
/// The main function is `compare_json()` which compares two JSON objects
/// and returns a list of differences.
///
/// Example:
///     >>> import fastjsondiff
///     >>> json1 = {"a": 1, "b": 2}
///     >>> json2 = {"a": 1, "b": 3}
///     >>> fastjsondiff.compare_json(json1, json2)
///     ['Value mismatch at b: Number(2) vs Number(3)']
fn fastjsondiff(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(compare_json, m)?)?;
    Ok(())
}
