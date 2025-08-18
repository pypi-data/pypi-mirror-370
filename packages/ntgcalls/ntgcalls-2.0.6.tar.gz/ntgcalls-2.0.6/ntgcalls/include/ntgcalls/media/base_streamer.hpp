//
// Created by Laky64 on 28/09/24.
//

#pragma once

#include <api/media_stream_interface.h>
#include <wrtc/models/frame_data.hpp>

namespace ntgcalls {

    class BaseStreamer {
    public:
        virtual ~BaseStreamer() = default;

        virtual void sendData(uint8_t* sample, size_t size, wrtc::FrameData additionalData) = 0;

        virtual webrtc::scoped_refptr<webrtc::MediaStreamTrackInterface> createTrack() = 0;
    };

} // ntgcalls
