FROM harbor.fybanks.com/library/jdk8:jmx AS builder

ARG PROXY=http://10.0.0.191:7890

RUN yum install -y \
        wget \
        autoconf \
        automake \
        bzip2 \
        bzip2-devel \
        cmake \
        freetype-devel \
        gcc \
        gcc-c++ \
        git \
        libtool \
        make \
        pkgconfig \
        zlib-devel \
        file \
    && mkdir -p /tmp/make

RUN cd /tmp/make \
    && printf '%s\n' \
        'https://www.nasm.us/pub/nasm/releasebuilds/2.15.05/nasm-2.15.05.tar.bz2' \
        'https://www.tortall.net/projects/yasm/releases/yasm-1.3.0.tar.gz' \
        'https://downloads.sourceforge.net/project/lame/lame/3.100/lame-3.100.tar.gz' \
        'https://archive.mozilla.org/pub/opus/opus-1.3.1.tar.gz' \
        > wget.txt \
    && wget \
        -e "https_proxy=${PROXY}" \
        -i wget.txt \
        --no-check-certificate \
    \
    && git config --global http.proxy "${PROXY}" \
    \
    # x264 固定 commit
    && git clone \
        https://code.videolan.org/videolan/x264.git \
        x264 \
    && cd /tmp/make/x264 \
    && git checkout 5db6aa6 \
    \
    # x265 固定 3.5
    && cd /tmp/make \
    && git clone \
        --branch 3.5 \
        --depth 1 \
        https://bitbucket.org/multicoreware/x265_git \
        x265_git \
    \
    # fdk-aac 固定 2.0.2
    && cd /tmp/make \
    && git clone \
        --branch v2.0.2 \
        --depth 1 \
        https://github.com/mstorsjo/fdk-aac.git \
        fdk-aac \
    \
    # libvpx 固定 1.11.0
    && cd /tmp/make \
    && git clone \
        --branch v1.11.0 \
        --depth 1 \
        https://chromium.googlesource.com/webm/libvpx.git \
        libvpx \
    \
    # FFmpeg 固定 4.4.1
    && cd /tmp/make \
    && git clone \
        --branch n4.4.1 \
        --depth 1 \
        https://github.com/FFmpeg/FFmpeg.git \
        ffmpeg-4.4.1


# ============================================================
# 编译
# ============================================================
RUN cd /tmp/make \
    \
    # NASM
    && tar -xjf nasm-2.15.05.tar.bz2 \
    && cd nasm-2.15.05 \
    && ./autogen.sh \
    && ./configure \
    && make -j4 \
    && make install \
    \
    # YASM
    && cd /tmp/make \
    && tar -xzf yasm-1.3.0.tar.gz \
    && cd yasm-1.3.0 \
    && ./configure \
    && make -j4 \
    && make install \
    \
    # x264 静态
    && cd /tmp/make/x264 \
    && ./configure \
        --enable-static \
        --disable-shared \
    && make -j4 \
    && make install \
    \
    # x265 静态
    && cd /tmp/make/x265_git/build/linux \
    && cmake \
        -G "Unix Makefiles" \
        -DENABLE_SHARED:BOOL=OFF \
        ../../source \
    && make -j4 \
    && make install \
    \
    # fdk-aac 静态
    && cd /tmp/make/fdk-aac \
    && autoreconf -fiv \
    && ./configure \
        --disable-shared \
        --enable-static \
    && make -j4 \
    && make install \
    \
    # LAME 静态
    && cd /tmp/make \
    && tar -xzf lame-3.100.tar.gz \
    && cd lame-3.100 \
    && ./configure \
        --disable-shared \
        --enable-static \
        --enable-nasm \
    && make -j4 \
    && make install \
    \
    # Opus 静态
    && cd /tmp/make \
    && tar -xzf opus-1.3.1.tar.gz \
    && cd opus-1.3.1 \
    && ./configure \
        --disable-shared \
        --enable-static \
    && make -j4 \
    && make install \
    \
    # libvpx 静态
    && cd /tmp/make/libvpx \
    && ./configure \
        --disable-examples \
        --disable-unit-tests \
        --enable-vp9-highbitdepth \
        --enable-static \
        --disable-shared \
        --as=yasm \
    && make -j4 \
    && make install \
    \
    # FFmpeg 4.4.1
    && cd /tmp/make/ffmpeg-4.4.1 \
    && PKG_CONFIG_PATH="/usr/local/lib/pkgconfig:/usr/local/lib64/pkgconfig" \
       ./configure \
        --pkg-config-flags="--static" \
        --extra-cflags="-I/usr/local/include" \
        --extra-ldflags="-L/usr/local/lib -L/usr/local/lib64" \
        --extra-libs="-lpthread -lm -ldl -lstdc++" \
        --enable-gpl \
        --enable-nonfree \
        --enable-libfdk_aac \
        --enable-libfreetype \
        --enable-libmp3lame \
        --enable-libopus \
        --enable-libvpx \
        --enable-libx264 \
        --enable-libx265 \
        --enable-parser=h264 \
    && make -j4 \
    && make install \
    \
    # Builder 验证
    && echo "========== FFmpeg Version ==========" \
    && /usr/local/bin/ffmpeg -version \
    && echo "========== FFmpeg LDD ==============" \
    && ldd /usr/local/bin/ffmpeg \
    && echo "========== FFprobe LDD =============" \
    && ldd /usr/local/bin/ffprobe \
    \
    && rm -rf /tmp/make \
    && yum clean all \
    && rm -rf /var/cache/yum/*


# ============================================================
# Stage 2: Runtime
# 与 Builder 完全相同的 Base Image
# ============================================================
FROM harbor.fybanks.com/library/jdk8:jmx

RUN yum install -y \
        freetype \
        zlib \
        bzip2-libs \
        libstdc++ \
    && yum clean all \
    && rm -rf /var/cache/yum/*


# 只复制最终程序
COPY --from=builder /usr/local/bin/ffmpeg /usr/local/bin/ffmpeg
COPY --from=builder /usr/local/bin/ffprobe /usr/local/bin/ffprobe

