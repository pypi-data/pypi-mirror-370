#pragma once

#if !STD_FROM_CHARS_FLOAT_SUPPORT
#include <fast_float/fast_float.h>
namespace surfio::parse_number {
using fast_float::from_chars;
}
#else
#include <charconv>
namespace surfio::parse_number {
using std::from_chars;
}
#endif
