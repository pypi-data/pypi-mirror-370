#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include "./fdexhand/include/dexhand.h"
namespace py = pybind11;
using namespace FdHand;

PYBIND11_MODULE(fdexhand, m) {
    py::enum_<Ret>(m, "Ret")
        .value("SUCCESS", Ret::SUCCESS)
        .value("FAIL", Ret::FAIL)
        .value("TIMEOUT", Ret::TIMEOUT)
        .export_values();
    
    py::enum_<HandType>(m, "HandType")
        .value("FDH_X", HandType::FDH_X)
        .value("FDH_L", HandType::FDH_L)
        .value("FDH_R", HandType::FDH_R)
        .export_values();

    py::enum_<CtrlType>(m, "CtrlType")
        .value("NONE", CtrlType::NONE)
        .value("POS_LOOP", CtrlType::POS_LOOP)
        .value("PD_LOOP", CtrlType::PD_LOOP)
        .value("POS_VEL_CUR_LOOP", CtrlType::POS_VEL_CUR_LOOP)
        .export_values();
    
    py::class_<HandCfg_t>(m, "HandCfg_t")
        .def(py::init<>())
        .def_readwrite("result", &HandCfg_t::result)
        .def_readwrite("type", &HandCfg_t::type)
        .def_readwrite("sn", &HandCfg_t::sn)
        .def_readwrite("ip", &HandCfg_t::ip)
        .def_readwrite("gateway", &HandCfg_t::gateway)
        .def_readwrite("mac", &HandCfg_t::mac);

    
    py::class_<CtrlCfg_t>(m, "CtrlCfg_t")
        .def(py::init<>())
        .def_readwrite("result", &CtrlCfg_t::result)
        .def_readwrite("PDKp", &CtrlCfg_t::PDKp)
        .def_readwrite("PDKd", &CtrlCfg_t::PDKd)
        .def_readwrite("PosKp", &CtrlCfg_t::PosKp)
        .def_readwrite("PosKi", &CtrlCfg_t::PosKi)
        .def_readwrite("PosKd", &CtrlCfg_t::PosKd)
        .def_readwrite("enWriteIntoChip", &CtrlCfg_t::enWriteIntoChip);

    py::class_<TimeoutCfg_t>(m, "TimeoutCfg_t")
        .def(py::init<>(), "Construct a TimeoutCfg with default values")
        .def_readwrite("result", &TimeoutCfg_t::result, "Result code")
        .def_readwrite("get_pos", &TimeoutCfg_t::get_pos, "Position get timeout (ms)")
        .def_readwrite("get_errorcode", &TimeoutCfg_t::get_errorcode, "Error code get timeout (ms)")
        .def_readwrite("get_matrix", &TimeoutCfg_t::get_matrix, "Matrix get timeout (ms)")
        .def_readwrite("get_pvc", &TimeoutCfg_t::get_pvc, "PVC get timeout (ms)");

    py::class_<DexHand>(m, "DexHand")
        .def(py::init<>())
        // .def("__del__", &DexHand::~DexHand)
        .def("init", &DexHand::init, py::arg("flg")=0, py::call_guard<py::gil_scoped_release>())
        .def("get_ip_list", &DexHand::get_ip_list, py::call_guard<py::gil_scoped_release>())
        .def("get_name", &DexHand::get_name, py::call_guard<py::gil_scoped_release>())
        .def("get_type", &DexHand::get_type, py::call_guard<py::gil_scoped_release>())
        .def("get_driver_ver", &DexHand::get_driver_ver, py::call_guard<py::gil_scoped_release>())
        .def("get_hardware_ver", &DexHand::get_hardware_ver, py::call_guard<py::gil_scoped_release>())
        .def("get_errorcode", &DexHand::get_errorcode, py::call_guard<py::gil_scoped_release>())
        .def("set_pos", &DexHand::set_pos, py::call_guard<py::gil_scoped_release>())
        .def("get_pos", &DexHand::get_pos, py::call_guard<py::gil_scoped_release>())
        .def("clear_errorcode", &DexHand::clear_errorcode, py::call_guard<py::gil_scoped_release>())
        .def("get_ts_matrix", &DexHand::get_ts_matrix, py::call_guard<py::gil_scoped_release>())
        .def("fast_set_pos", &DexHand::fast_set_pos, py::call_guard<py::gil_scoped_release>())
        .def("set_hand_config", &DexHand::set_hand_config, py::call_guard<py::gil_scoped_release>())
        .def("get_hand_config", &DexHand::get_hand_config, py::call_guard<py::gil_scoped_release>())
        .def("set_controller_config", &DexHand::set_controller_config, py::call_guard<py::gil_scoped_release>())
        .def("get_controller_config", &DexHand::get_controller_config, py::call_guard<py::gil_scoped_release>())
        .def("get_ctrl_mode", &DexHand::get_ctrl_mode, py::call_guard<py::gil_scoped_release>())
        .def("reboot", (Ret (DexHand::*)()) & DexHand::reboot, py::call_guard<py::gil_scoped_release>())
        .def("reboot", (Ret (DexHand::*)(std::string)) & DexHand::reboot, py::call_guard<py::gil_scoped_release>())
        .def("enable", (Ret (DexHand::*)()) & DexHand::enable, py::call_guard<py::gil_scoped_release>())
        .def("enable", (Ret (DexHand::*)(std::string)) & DexHand::enable, py::call_guard<py::gil_scoped_release>())
        .def("disable", (Ret (DexHand::*)()) & DexHand::disable, py::call_guard<py::gil_scoped_release>())
        .def("disable", (Ret (DexHand::*)(std::string)) & DexHand::disable, py::call_guard<py::gil_scoped_release>())
        .def("get_pvc", &DexHand::get_pvc, py::call_guard<py::gil_scoped_release>())
        .def("set_pvc", &DexHand::set_pvc, py::call_guard<py::gil_scoped_release>())
        .def("get_pvc_relative", &DexHand::get_pvc_relative, py::call_guard<py::gil_scoped_release>())
        .def("set_pvc_relative", &DexHand::set_pvc_relative, py::call_guard<py::gil_scoped_release>())
        .def("set_pd_params", &DexHand::set_pd_params, py::call_guard<py::gil_scoped_release>())
        .def("set_ctrl_mode", &DexHand::set_ctrl_mode, py::call_guard<py::gil_scoped_release>())
        .def("set_timeout_max", &DexHand::set_timeout_max, py::call_guard<py::gil_scoped_release>())
        .def("get_timeout_max", &DexHand::get_timeout_max, py::call_guard<py::gil_scoped_release>())
        ;
}
