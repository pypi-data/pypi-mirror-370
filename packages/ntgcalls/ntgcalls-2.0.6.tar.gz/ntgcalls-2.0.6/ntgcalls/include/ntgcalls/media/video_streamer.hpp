//
// Created by Laky64 on 12/08/2023.
//

#pragma once

#include <wrtc/wrtc.hpp>
#include <ntgcalls/media/video_sink.hpp>
#include <ntgcalls/media/base_streamer.hpp>

namespace ntgcalls {
    class VideoStreamer final : public VideoSink, public BaseStreamer {
        std::unique_ptr<wrtc::RTCVideoSource> video;

    public:
        VideoStreamer();

        ~VideoStreamer() override;

        webrtc::scoped_refptr<webrtc::MediaStreamTrackInterface> createTrack() override;

        void sendData(uint8_t* sample, size_t size, wrtc::FrameData additionalData) override;
    };
}

