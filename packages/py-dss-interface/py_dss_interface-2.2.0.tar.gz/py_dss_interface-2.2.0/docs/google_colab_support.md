# Google Colab Support

py-dss-interface now includes automatic support for Google Colab environments, making it easier to use OpenDSS in educational and research contexts.

## Automatic Detection

The library automatically detects when it's running in Google Colab and uses a pre-built OpenDSS library specifically compiled for the Colab environment. This eliminates the need for users to build OpenDSS from source.

## How It Works

1. **Environment Detection**: The library checks if the `google.colab` module is available
2. **Automatic Path Selection**: 
   - **Google Colab**: Uses `opendss_official/linux/google_colab/`
   - **Regular Linux**: Uses `opendss_official/linux/cpp/` (requires building)
   - **Windows**: Uses appropriate Windows version (delphi or cpp)
3. **Error Handling**: If the Google Colab version fails, it provides helpful error messages and instructions

## Usage

Simply import and use py-dss-interface as usual:

```python
from py_dss_interface import DSS

# Automatically selects the appropriate OpenDSS library
dss = DSS(print_dss_info=True)

# Use OpenDSS normally
dss.text("New Circuit.Test")
dss.text("solve")
```

## Backend Information

When `print_dss_info=True` is used, the library will show which backend is being used:
- `Linux-C++-GoogleColab`: Using the pre-built Google Colab version
- `Linux-C++`: Using the standard Linux version
- `Windows-Delphi`: Using Windows Delphi version
- `Windows-C++`: Using Windows C++ version

## Benefits

- **No Building Required**: Users don't need to build OpenDSS from source
- **Faster Setup**: Immediate availability in Google Colab
- **Educational Friendly**: Perfect for teaching and learning OpenDSS
- **Automatic Fallback**: Robust error handling if the pre-built version fails

## Technical Details

The pre-built library is compiled for Ubuntu 22.04 (jammy) and includes all necessary dependencies. The library files are:

- `libOpenDSSC.so`: Main OpenDSS library
- `libklusolve_all.so*`: KLUSolve dependencies

## Troubleshooting

If you encounter issues with the Google Colab version:

1. The library will show an error message with instructions
2. You can build OpenDSS from source following the example at: https://github.com/PauloRadatz/py_dss_interface/blob/master/examples/1_py_dss_interfece_in_google_colab.ipynb
3. Contact Paulo Radatz at paulo.radatz@gmail.com for support

For more information, see the examples in the `examples/` directory.
