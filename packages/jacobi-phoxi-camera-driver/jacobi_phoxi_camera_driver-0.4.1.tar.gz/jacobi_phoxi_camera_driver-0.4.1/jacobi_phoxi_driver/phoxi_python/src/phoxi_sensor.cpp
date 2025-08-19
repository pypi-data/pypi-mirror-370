#include <iostream>

#include <phoxi_sensor.h>


PhoXiSensor::PhoXiSensor(const std::string& device_name): device_name(device_name) { }

PhoXiSensor::~PhoXiSensor() {
    stop();
}

bool PhoXiSensor::start() {
    return connect() && device->StartAcquisition();
}

bool PhoXiSensor::connect() {
    pho::api::PhoXiFactory factory;

    // Check if the PhoXi Control Software is running
    if (!factory.isPhoXiControlRunning()) {
        std::cout << "PhoXi Control Software is not running" << std::endl;
        return false;
    }

    // Get List of available devices on the network
    const std::vector<pho::api::PhoXiDeviceInformation> device_list = factory.GetDeviceList();
    if (device_list.empty()) {
        std::cout << "PhoXi Factory has found 0 devices" << std::endl;
        return false;
    }

    if (device_name.empty()) {
        // If no device was given, print all and connect to first attached
        std::cout << "The following devices are available:" << std::endl;
        for (const auto& d: device_list) {
            std::cout << "- " << d.Name << std::endl;
        }

        device = factory.CreateAndConnectFirstAttached();

    } else {
        // If device name was given, extract hardware id from that
        std::string hardware_id = device_name;
        for (const auto& d: device_list) {
            if (device_name == d.Name) {
                hardware_id = d.HWIdentification;
                break;
            }
        }

        device = factory.CreateAndConnect(hardware_id, 5000);
    }

    // Check if device was created
    if (!device || !device->isConnected()) {
        std::cout << "Failed to connect to PhoXi device." << std::endl;
        return false;
    }

    device->CapturingSettings->AmbientLightSuppression = true;
    device->TriggerMode = pho::api::PhoXiTriggerMode::Software;

    return true;
}

void PhoXiSensor::stop() {
    if (!device) {
        return;
    }

    if (device->isAcquiring()) {
        device->StopAcquisition();
    }

    device->Disconnect(true, false);
}

bool PhoXiSensor::frames() {
    if (!device || !device->isConnected()) {
        return false;
    }

    device->ClearBuffer();
    if (!device->isAcquiring()) {
        std::cout << "Your device is not started for acquisition!" << std::endl;
        return false;
    }

    last_frame_id = device->TriggerFrame();
    if (last_frame_id < 0) {
        std::cout << "Trigger was unsuccessful!" << std::endl;
        return false;
    }

    frame = device->GetSpecificFrame(last_frame_id, 5000);
    if (!frame) {
        std::cout << "Failed to retrieve the frame!" << std::endl;
        return false;
    }

    const auto& camera_matrix = frame->Info.CameraMatrix;
    intrinsics.fx = camera_matrix[0][0];
    intrinsics.fy = camera_matrix[1][1];
    intrinsics.cx = camera_matrix[0][2];
    intrinsics.cy = camera_matrix[1][2];
    intrinsics.distortion_coefficients = frame->Info.DistortionCoefficients;
    return true;
}

std::shared_future<bool> PhoXiSensor::frames_async() {
    return std::async(std::launch::async, &PhoXiSensor::frames, this);
}

bool PhoXiSensor::save_last_frame(const std::filesystem::path& path) {
    if (last_frame_id == -1) {
        return false;
    }
    return device->SaveLastOutput(path.string(), last_frame_id);
}

std::vector<std::vector<float>> PhoXiSensor::get_depth_map() const {
    const int width = frame->DepthMap.Size.Width;
    const int height = frame->DepthMap.Size.Height;

    std::vector<std::vector<float>> depth_map;
    depth_map.resize(height);
    for (size_t i = 0; i < height; i++) {
        depth_map[i].resize(width);

        for (size_t j = 0; j < width; j++) {
            depth_map[i][j] = frame->DepthMap.At(i, j) / 1000.0;  // from [mm] to [m]
        }
    }
    return depth_map;
}

std::vector<std::vector<float>> PhoXiSensor::get_texture() const {
    const int width = frame->Texture.Size.Width;
    const int height = frame->Texture.Size.Height;

    std::vector<std::vector<float>> texture;
    texture.resize(height);
    for (size_t i = 0; i < height; i++) {
        texture[i].resize(width);

        for (size_t j = 0; j < width; j++) {
            texture[i][j] = frame->Texture.At(i, j);
        }
    }
    return texture;
}

// std::vector<std::vector<float>> PhoXiSensor::get_point_cloud() const {
//     const int width = frame->PointCloud.Size.Width;
//     const int height = frame->PointCloud.Size.Height;
//     std::vector<std::vector<float>> cloud;
//     cloud.resize(height);
//     for (size_t i = 0; i < height; i++) {
//         cloud[i].resize(width);

//         for (size_t j = 0; j < width; j++) {
//             cloud[i][j] = frame->PointCloud.At(i, j) / 1000.0;
//         }
//     }

//     return cloud;
// }

void PhoXiSensor::print_device_info_list(const std::vector<pho::api::PhoXiDeviceInformation>& device_list) {
    for (size_t i = 0; i < device_list.size(); ++i) {
        std::cout << "Device: " << i << std::endl;
        print_device_info(device_list[i]);
    }
}

void PhoXiSensor::print_device_info(const pho::api::PhoXiDeviceInformation& DeviceInfo) {
    std::cout << "  Name:                    " << DeviceInfo.Name << std::endl;
    std::cout << "  Hardware Identification: " << DeviceInfo.HWIdentification << std::endl;
    std::cout << "  Type:                    " << std::string(DeviceInfo.Type) << std::endl;
    std::cout << "  Firmware version:        " << DeviceInfo.FirmwareVersion << std::endl;
    std::cout << "  Variant:                 " << DeviceInfo.Variant << std::endl;
    std::cout << "  IsFileCamera:            " << (DeviceInfo.IsFileCamera ? "Yes" : "No") << std::endl;
    std::cout << "  Feature-Alpha:           " << (DeviceInfo.CheckFeature("Alpha") ? "Yes" : "No") << std::endl;
    std::cout << "  Feature-Color:           " << (DeviceInfo.CheckFeature("Color") ? "Yes" : "No") << std::endl;
    std::cout << "  Status:                  "
        << (DeviceInfo.Status.Attached ? "Attached to PhoXi Control. " : "Not Attached to PhoXi Control. ")
        << (DeviceInfo.Status.Ready ? "Ready to connect" : "Occupied")
        << std::endl << std::endl;
}

void PhoXiSensor::print_frame_info(const pho::api::FrameInfo& info) {
    std::cout << "  Frame Info: " << std::endl;
    std::cout << "\tFrame Index: "                  << info.FrameIndex << std::endl;
    std::cout << "\tFrame Timestamp: "              << info.FrameTimestamp << " ms" << std::endl;
    std::cout << "\tFrame Acquisition duration: "   << info.FrameDuration << " ms" << std::endl;
    std::cout << "\tFrame Computation duration: "   << info.FrameComputationDuration << " ms" << std::endl;
    std::cout << "\tFrame Transfer duration: "      << info.FrameTransferDuration << " ms" << std::endl;
    std::cout << "\tFrame Acquisition time (PTP): " << info.FrameStartTime.TimeAsString("%Y-%m-%d %H:%M:%S") << std::endl;
    std::cout << "\tSensor Position: [" << info.SensorPosition.x << "; " << info.SensorPosition.y << "; " << info.SensorPosition.z << "]" << std::endl;
    std::cout << "\tTotal scan count: "         << info.TotalScanCount << std::endl;
    std::cout << "\tColor Camera Position: ["   << info.ColorCameraPosition.x << "; " << info.ColorCameraPosition.y << "; " << info.ColorCameraPosition.z << "]" << std::endl;
    std::cout << "\tCurrent Camera Position: [" << info.CurrentCameraPosition.x << "; " << info.CurrentCameraPosition.y << "; " << info.CurrentCameraPosition.z << "]" << std::endl;
    std::cout << "\tFilenamePath: "             << info.FilenamePath << std::endl;
    std::cout << "\tHWIdentification: "         << info.HWIdentification << std::endl;
}

template<class T>
void print_element(const std::string& name, const T& data) {
    std::cout << "\t" << name << " size: (" << data.Size.Width  << ", " << data.Size.Height << ") type: " << data.GetElementName() << std::endl;
}

void PhoXiSensor::print_frame_data(const pho::api::PFrame& frame_) {
    if (frame_->Empty()) {
        std::cout << "Frame is empty.";
        return;
    }
    std::cout << "  Frame data: " << std::endl;
    if (!frame_->PointCloud.Empty()) {
        print_element("PointCloud", frame_->PointCloud);
    }
    if (!frame_->NormalMap.Empty()) {
        print_element("NormalMap", frame_->NormalMap);
    }
    if (!frame_->DepthMap.Empty()) {
        print_element("DepthMap", frame_->DepthMap);
    }
    if (!frame_->ConfidenceMap.Empty()) {
        print_element("ConfidenceMap", frame_->ConfidenceMap);
    }
    if (!frame_->Texture.Empty()) {
        print_element("Texture", frame_->Texture);
    }
    if (!frame_->TextureRGB.Empty()) {
        print_element("TextureRGB", frame_->TextureRGB);
    }
    if (!frame_->ColorCameraImage.Empty()) {
        print_element("ColorCameraImage", frame_->ColorCameraImage);
    }
}
