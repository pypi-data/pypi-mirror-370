<img src="https://raw.githubusercontent.com/pytgcalls/ntgcalls/master/.github/images/banner.png" alt="pytgcalls logo" />
<p align="center">
    <b>A Native Implementation of Telegram Calls in a seamless way.</b>
    <br>
    <a href="https://github.com/pytgcalls/ntgcalls/tree/master/examples">
        Examples
    </a>
    •
    <a href="https://pytgcalls.github.io/">
        Documentation
    </a>
    •
    <a href="https://pypi.org/project/ntgcalls/">
        PyPi
    </a>
    •
    <a href="https://github.com/pytgcalls/ntgcalls/releases">
        Releases
    </a>
    •
    <a href="https://t.me/pytgcallsnews">
        Channel
    </a>
    •
    <a href="https://t.me/pytgcallschat">
        Chat
    </a>
</p>

# NTgCalls [![PyPI - Version](https://img.shields.io/pypi/v/ntgcalls?logo=python&logoColor=%23959DA5&label=pypi&labelColor=%23282f37)](https://pypi.org/project/ntgcalls/) [![Downloads](https://img.shields.io/pepy/dt/ntgcalls?logoColor=%23959DA5&labelColor=%23282f37&color=%2328A745)](https://pepy.tech/project/ntgcalls)
NTgCalls is a lightweight open-source library for media streaming in Telegram calls. Built from scratch in C++ with WebRTC & Boost, it prioritizes accessibility to developers and resource efficiency.

|                                                                                     Powerful                                                                                      |                                                                                            Simple                                                                                            |                                                                                                   Light                                                                                                    |
|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
| <img src="https://raw.githubusercontent.com/pytgcalls/ntgcalls/master/.github/images/fast.gif" width=150 alt="Fast Logo"/><br>Built from scratch in C++ using Boost and libwebrtc | <img src="https://raw.githubusercontent.com/pytgcalls/ntgcalls/master/.github/images/simple.gif" width=150 alt="Simple Logo"/><br>Simple Python, GO, C Bindings and Java for Android SDK<br> | <img src="https://raw.githubusercontent.com/pytgcalls/ntgcalls/master/.github/images/light.gif" width=150 alt="Light logo"/><br>We removed anything that could burden the library, including <b>NodeJS</b> |

## Build Status
| Architecture |                                                                   Windows                                                                   |                                                                Linux                                                                |                                                                  MacOS                                                                  |
|:------------:|:-------------------------------------------------------------------------------------------------------------------------------------------:|:-----------------------------------------------------------------------------------------------------------------------------------:|:---------------------------------------------------------------------------------------------------------------------------------------:|
|    x86_64    |   ![BUILD](https://img.shields.io/badge/build-passing-dark_green?logo=windows11&logoColor=%23959DA5&labelColor=%23282f37&color=%2328A745)   | ![BUILD](https://img.shields.io/badge/build-passing-dark_green?logo=linux&logoColor=%23959DA5&labelColor=%23282f37&color=%2328A745) | ![BUILD](https://img.shields.io/badge/build-unsupported-dark_green?logo=apple&logoColor=%23959DA5&labelColor=%23282f37&color=%23959DA5) |
|    ARM64     | ![BUILD](https://img.shields.io/badge/build-unsupported-dark_green?logo=windows11&logoColor=%23959DA5&labelColor=%23282f37&color=%23959DA5) | ![BUILD](https://img.shields.io/badge/build-passing-dark_green?logo=linux&logoColor=%23959DA5&labelColor=%23282f37&color=%2328A745) |   ![BUILD](https://img.shields.io/badge/build-passing-dark_green?logo=apple&logoColor=%23959DA5&labelColor=%23282f37&color=%2328A745)   |

## Features
- Pre-built binaries for macOS (arm64-v8a), Linux (x86_64, arm64-v8a), Windows (x86_64), and Android (x86, 86_64, arm64-v8a, armv7)
- Call flexibility: Group and private call support
- Media controls: pause/resume and mute/unmute
- Codec compatibility: H.264, HEVC (H.265), VP8, VP9, AV1, AAC, MP3, Opus
- Content sharing: Screen streaming, Microphone and Camera streaming
- Pre-built wheels for Python & AAR SDK library for Android

## Compiling

### Python Bindings
NTgCalls includes Python bindings for seamless integration. Follow these steps to compile it with Python Bindings:
1. Ensure you are in the root directory of the NTgCalls project.
2. Run the following command to install the Py Bindings:

   ```shell
   python3 setup.py install
   ```
### Go Bindings
> [!WARNING]
> Static linking for Windows is not supported yet since our library is built with MSVC and Go uses MinGW for static linking.
> More info can be found [here](https://github.com/golang/go/issues/63903)

NTgCalls includes Go Bindings, enabling seamless integration with Go. Follow these steps to compile it with Go Bindings:
1. There is an example project for Go in `./examples/go/` directory, ensure you are in that directory
2. Prerequisites for building are the same as for building a library itself and can be found [here](https://pytgcalls.github.io/NTgCalls/Build%20Guide#Installing=Prerequisites)
3. Download **shared** or **static** release of the library from https://github.com/pytgcalls/ntgcalls/releases
4. Copy `ntgcalls.h` file into `./examples/go/ntgcalls/` directory
5. The rest of the files should be copied to `./examples/go/` directory
    * `ntgcalls.dll` or `ntgcalls.lib` files in case of Windows amd64
    * `libntgcalls.so` or `libntgcalls.a` files in case of Linux amd64
    * `libntgcalls.dylib` or `libntgcalls.a` files in case of macOS
6. Then in `./examples/go/` directory run `go build` or `go run .` with CGO_ENABLED=1 env variable set
    * `$env:CGO_ENABLED=1; go run .` for Windows PowerShell
    * `CGO_ENABLED=1 go run .` for UNIX


### C Bindings
For developers looking to use NTgCalls with C and C++, we provide C Bindings. Follow these steps to compile it with C Bindings:
1. Ensure you are in the root directory of the NTgCalls project.
2. Run the following command to generate the library:
   ```shell
   # Static library
   python3 setup.py build_lib --static
   
   # Shared library
   python3 setup.py build_lib --shared
   ```
3. Upon successful execution, a library will be generated in the "shared-output" or "static-output" directory, depending on the chosen option.
   Now you can use this library to develop applications with NTgCalls.
4. To include the necessary headers in your C/C++ projects, you will find the "include" folder in the "shared-output" or "static-output" directory.
   Use this folder by including the required header files.

## Key Contributors
* <b><a href="https://github.com/Laky-64">@Laky-64</a> (DevOps Engineer, Software Architect, Porting Engineer):</b>
    * Played a crucial role in developing NTgCalls.
    * Created the Python Bindings that made the library accessible to Python developers.
    * Developed the C Bindings, enabling the library's use in various environments.
* <b><a href="https://github.com/dadadani">@dadadani</a> (Senior C++ Developer, Performance engineer):</b>
    * Contributed to setting up CMakeLists and integrating with pybind11,
      greatly simplifying the library's usage for C++ developers.
* <b><a href="https://github.com/kuogi">@kuogi</a> (Senior UI/UX designer, Documenter):</b>
    * As a Senior UI/UX Designer, Kuogi has significantly improved the user interface of our documentation,
      making it more visually appealing and user-friendly.
    * It Has also played a key role in writing and structuring our documentation, ensuring that it is clear,
      informative, and accessible to all users.
* <b><a href="https://github.com/vrumger">@vrumger</a> (Mid-level NodeJS Developer):</b>
    * Avrumy has made important fixes and enhancements to the WebRTC component of the library,
      improving its stability and performance.

## Junior Developers
* <b><a href="https://github.com/TuriOG">@TuriOG</a> (Junior Python Developer):</b>
    * Currently working on integrating NTgCalls into <a href="//github.com/pytgcalls/pytgcalls">PyTgCalls</a>, an important step
      in expanding the functionality and usability of the library.
* <b><a href="https://github.com/doggyhaha">@doggyhaha</a> (Junior DevOps, Tester):</b>
    * Performs testing of NTgCalls on Linux to ensure its reliability and compatibility.
    * Specializes in creating and maintaining GitHub Actions, focusing on automation tasks.
* <b><a href="https://github.com/tappo03">@tappo03</a> (Junior Go Developer, Tester):</b>
    * Performs testing of NTgCalls on Windows to ensure its reliability and compatibility.
    * It Is in the process of integrating NTgCalls into a Go wrapper, further enhancing the library's
      versatility and accessibility.

## Special Thanks
* <b><a href="https://github.com/shiguredo">@shiguredo</a>:</b>
  We extend our special thanks to 時雨堂 (shiguredo) for their invaluable assistance in integrating the WebRTC component. Their contributions,
  using the Sora C++ SDK, have been instrumental in enhancing the functionality of our library.

* <b><a href="https://github.com/evgeny-nadymov">@evgeny-nadymov</a>:</b>
  A heartfelt thank you to Evgeny Nadymov for graciously allowing us to use their code from telegram-react.
  His contribution has been pivotal to the success of this project.

* <b><a href="https://github.com/morethanwords">@morethanwords</a>:</b>
  We extend our special thanks to morethanwords for their invaluable help in integrating the connection to WebRTC with Telegram Web K.
  Their assistance has been instrumental in enhancing the functionality of our library.

* <b><a href="https://github.com/MarshalX">@MarshalX</a>:</b> for their generous assistance in answering questions and providing insights regarding WebRTC.

* <b><a href="https://github.com/LyzCoote">@LyzCoote</a>:</b> for providing an ARM64 Server and allowing us to build an image with clang-18 preinstalled on manylinux2014 arm64.

_We would like to extend a special thanks to <b><a href='https://github.com/null-nick'>@null-nick</a></b>
and <b><a href='https://github.com/branchscope'>@branchscope</a></b> for their valuable contributions to the testing phase of the library and to
<b><a href='https://github.com/SadLuffy'>@SadLuffy</a></b> for his assistance as a copywriter.
Their dedication to testing and optimizing the library has been instrumental in its success._

_Additionally, we extend our gratitude to all contributors for their exceptional work in making this project a reality._
