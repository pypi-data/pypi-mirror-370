#pragma once

#include <filesystem>
#include <future>
#include <string>
#include <vector>

#include "PhoXi.h"


class PhoXiSensor {
    pho::api::PPhoXi device;
    pho::api::PFrame frame;

    int last_frame_id {-1};

    // Print helpers
    static void print_device_info_list(const std::vector<pho::api::PhoXiDeviceInformation>& device_list);
    static void print_device_info(const pho::api::PhoXiDeviceInformation& device_info);
    static void print_frame_data(const pho::api::PFrame& frame);
    static void print_frame_info(const pho::api::FrameInfo& info);

public:
    //! Name of the Photoneo device
    std::string device_name;

    struct Intrinsics {
        double fx, fy;
        double cx, cy;
        std::vector<double> distortion_coefficients;
    } intrinsics;

    //! Connect to a PhoXi sensor
    explicit PhoXiSensor(const std::string& device_name);
    ~PhoXiSensor();

    //! Start the sensor.
    bool start();

    //! Stop the sensor.
    void stop();

    //! Connect the sensor.
    bool connect();

    //! Retrieve a frame from the sensor.
    bool frames();

    //! Retrieve a frame from the sensor asynchronously.
    std::shared_future<bool> frames_async();

    //! Saves the last frame at the given path.
    bool save_last_frame(const std::filesystem::path& path);

    //! Get the depth map.
    std::vector<std::vector<float>> get_depth_map() const;

    //! Get the texture.
    std::vector<std::vector<float>> get_texture() const;

    //! Get the point cloud.
    // std::vector<std::vector<float>> get_point_cloud() const;
};
