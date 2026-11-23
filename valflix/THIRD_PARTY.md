# ValFlix: open-source components

ValFlix's own code is not open source. Its players include the open-source libraries below, each
under its own licence.

## Backup player: mpv and FFmpeg (LGPL)

When a TV can't decode a video itself, ValFlix plays it with **mpv**, which brings its own
**FFmpeg**. Both are built **without their GPL-only parts**, so they are covered by the GNU Lesser
General Public License:

| Library | Version | Licence |
| --- | --- | --- |
| mpv (libmpv) | 0.42.0 | LGPL 2.1 or later (built with `-Dgpl=false`) |
| FFmpeg | 9.0.2 | LGPL 3 or later (built without `--enable-gpl`) |
| libplacebo | 7.387.0 | LGPL 2.1 or later |
| FriBidi | 1.0.18 | LGPL 2.1 or later |
| libass | 0.17.5 | ISC |
| HarfBuzz | 15.1.0 | Old MIT |
| FreeType | 2.15.0 | FreeType License |
| fontconfig | 2.18.3 | fontconfig licence (permissive) |
| libunibreak | 8.0 | zlib |
| libxml2 | 2.15.4 | MIT |
| dav1d | 1.5.4 | BSD 2-Clause |
| Lua | 5.2.4 | MIT |
| curl | 8.23.0 | curl licence |
| mbedTLS | 3.6.7 | Apache 2.0 |
| libmpv-android (Java/JNI wrapper and build scripts) | v1.1.0 | MIT |

They ship as separate shared libraries inside the app (`libmpv.so`, `libavcodec.so`,
`libavformat.so`, `libavutil.so`, `libswresample.so`, `libswscale.so`, `libavfilter.so`,
`libavdevice.so`, `libplayer.so`), which you may replace with your own builds of the same versions.

### Source code and how ValFlix builds them

The libraries are built from unmodified upstream sources with the build scripts of
[libmpv-android v1.1.0](https://github.com/jarnedemeulemeester/libmpv-android/tree/v1.1.0)
(commit `85a2445098b7cba99576c2963b1417b17b4debdd`), which download each library's source at the
versions above (see `buildscripts/include/depinfo.sh` there). ValFlix changes only these build
settings:

1. `buildscripts/scripts/ffmpeg.sh`: `--enable-{gpl,version3}` becomes `--enable-version3` (LGPL 3),
   and the GPL-only `libpostproc` is not built.
2. `buildscripts/scripts/mpv.sh`: `-Dgpl=false` is added to mpv's meson options (LGPL).
3. Only the `armeabi-v7a` and `arm64-v8a` architectures are built.

Then, in `buildscripts`: `./download.sh`, `./patch.sh`, `./build.sh --arch armv7l mpv`,
`./build.sh --arch arm64 mpv`, `./build.sh -n`.

Upstream sources: [mpv](https://github.com/mpv-player/mpv), [FFmpeg](https://ffmpeg.org/download.html),
[libplacebo](https://code.videolan.org/videolan/libplacebo), [FriBidi](https://github.com/fribidi/fribidi),
[libass](https://github.com/libass/libass). To get the exact source ValFlix uses, ask via the
[adamsbuilds repo](https://github.com/adamsbuilds/repo) and it will be provided.

## Main player

| Library | Version | Licence |
| --- | --- | --- |
| AndroidX Media3 (ExoPlayer) | 1.9.4 | Apache 2.0 |
| Media3 AV1 extension with dav1d | 1.9.4 / dav1d 1.5.1 | Apache 2.0 / BSD 2-Clause |
| Jellyfin Media3 FFmpeg audio decoder | 1.9.0+1 | FFmpeg built as LGPL |
