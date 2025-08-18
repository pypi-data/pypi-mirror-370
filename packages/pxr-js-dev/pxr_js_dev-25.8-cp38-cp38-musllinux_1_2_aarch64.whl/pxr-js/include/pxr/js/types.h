// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_JS_TYPES_H
#define PXR_JS_TYPES_H

/// \file js/types.h

#include "pxr/js/pxr.h"

#include <map>
#include <string>
#include <vector>

JS_NAMESPACE_OPEN_SCOPE

class JsValue;
typedef std::map<std::string, JsValue> JsObject;
typedef std::vector<JsValue> JsArray;

JS_NAMESPACE_CLOSE_SCOPE

#endif // PXR_JS_TYPES_H
