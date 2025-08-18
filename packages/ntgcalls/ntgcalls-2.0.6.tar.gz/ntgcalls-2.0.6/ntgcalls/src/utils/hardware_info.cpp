//
// Created by Laky64 on 02/03/2024.
//

#include <ntgcalls/utils/hardware_info.hpp>

#if defined(IS_LINUX) || defined(IS_ANDROID)
#include <unistd.h>
#elif IS_MACOS
#include <sys/resource.h>
#endif

namespace ntgcalls {
    HardwareInfo::HardwareInfo() {
#ifdef IS_WINDOWS
        FILETIME ftime, fsys, fuser;
        SYSTEM_INFO sysInfo;
        GetSystemInfo(&sysInfo);
        numProcessors = static_cast<int>(sysInfo.dwNumberOfProcessors);
        GetSystemTimeAsFileTime(&ftime);
        memcpy(&lastCPU, &ftime, sizeof(FILETIME));

        self = GetCurrentProcess();
        GetProcessTimes(self, &ftime, &ftime, &fsys, &fuser);
        memcpy(&lastSysCPU, &fsys, sizeof(FILETIME));
        memcpy(&lastUserCPU, &fuser, sizeof(FILETIME));
#elif IS_MACOS
        size_t len = sizeof(numProcessors);
        sysctlbyname("hw.ncpu", &numProcessors, &len, NULL, 0);
        struct rusage usage;
        getrusage(RUSAGE_SELF, &usage);
        lastCPU = usage.ru_utime.tv_sec * 1000000 + usage.ru_utime.tv_usec + usage.ru_stime.tv_sec * 1000000 + usage.ru_stime.tv_usec;
        lastSysCPU = usage.ru_stime.tv_sec * 1000000 + usage.ru_stime.tv_usec;
        lastUserCPU = usage.ru_utime.tv_sec * 1000000 + usage.ru_utime.tv_usec;
#else
        numProcessors = static_cast<int>(sysconf(_SC_NPROCESSORS_ONLN));
        tms timeSample{};
        lastCPU = times(&timeSample);
        lastSysCPU = timeSample.tms_stime;
        lastUserCPU = timeSample.tms_utime;
#endif
    }

    double HardwareInfo::getCpuUsage() {
        double percent;
#ifdef IS_WINDOWS
        FILETIME ftime, fsys, fuser;
        ULARGE_INTEGER now, sys, user;

        GetSystemTimeAsFileTime(&ftime);
        memcpy(&now, &ftime, sizeof(FILETIME));

        GetProcessTimes(self, &ftime, &ftime, &fsys, &fuser);
        memcpy(&sys, &fsys, sizeof(FILETIME));
        memcpy(&user, &fuser, sizeof(FILETIME));
        percent = static_cast<double>(sys.QuadPart - lastSysCPU.QuadPart + user.QuadPart - lastUserCPU.QuadPart);
        percent /= static_cast<double>(now.QuadPart - lastCPU.QuadPart);
        percent /= numProcessors;
        lastCPU = now;
        lastUserCPU = user;
        lastSysCPU = sys;
#elif IS_MACOS
        struct rusage usage;
        getrusage(RUSAGE_SELF, &usage);
        clock_t now = (usage.ru_utime.tv_sec + usage.ru_stime.tv_sec) * 1000000 + (usage.ru_utime.tv_usec + usage.ru_stime.tv_usec);
        if (now <= lastCPU || usage.ru_stime.tv_sec < lastSysCPU || usage.ru_utime.tv_sec < lastUserCPU) {
            percent = -1.0;
        } else {
            percent = static_cast<double>(usage.ru_stime.tv_sec - lastSysCPU + usage.ru_utime.tv_sec - lastUserCPU);
            percent /= static_cast<double>(now - lastCPU);
            percent /= numProcessors;
            percent *= 100;
        }
        lastCPU = now;
        lastSysCPU = usage.ru_stime.tv_sec;
        lastUserCPU = usage.ru_utime.tv_sec;
#else
        tms timeSample{};
        auto now = times(&timeSample);
        if (now <= lastCPU || timeSample.tms_stime < lastSysCPU || timeSample.tms_utime < lastUserCPU) {
            percent = -1.0;
        } else{
            percent = static_cast<double>(timeSample.tms_stime - lastSysCPU + timeSample.tms_utime - lastUserCPU);
            percent /= static_cast<double>(now - lastCPU);
            percent /= numProcessors;
            percent *= 100;
        }
        lastCPU = now;
        lastSysCPU = timeSample.tms_stime;
        lastUserCPU = timeSample.tms_utime;
#endif
        return percent;
    }

    uint16_t HardwareInfo::getCoreCount() const {
        return numProcessors;
    }
} // ntgcalls