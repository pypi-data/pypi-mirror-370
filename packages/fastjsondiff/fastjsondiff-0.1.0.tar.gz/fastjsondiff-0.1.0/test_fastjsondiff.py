#!/usr/bin/env python3

import fastjsondiff


def test_basic_comparison():
    print("Testing basic JSON comparison...")

    # Test data
    json1 = {
        "name": "create_testbench_for_current_mirror",
        "args": {
            "netlist_name": "001_02_0.txt",
            "current_mirror_name": "current_mirror_2",
            "testbench_description": "Testbench for impedance analysis of modified current mirror 2",
            "testbench_name": "current_mirror_2_impedance_test.scs",
            "ac_analysis_settings": {
                "start_freq": 10000,
                "stop_freq": 10000000,
                "steps": 3,
                "step_type": "dec",
            },
            "noise_analysis_settings": {
                "start_freq": 1000,
                "stop_freq": 10000000,
                "steps": 10,
                "step_type": "dec",
            },
            "voltage_source_settings": {
                "power_supply_voltage": 1.8,
                "bias_current": 1e-5,
                "primary_cascode_dc_bias": 0.8,
                "primary_cascode_ac_stimulus": 1,
                "secondary_voltage_source_dc": 0.5,
                "secondary_voltage_source_ac": 1,
            },
            "analysis_types": {"ac_analysis": True, "noise_analysis": False},
        },
        "id": "call_jBf9Gg0IQQj0XSTVnZVyO16p",
        "type": "tool_call",
    }
    json2 = {
        "name": "create_testbench_for_current_mirror",
        "args": {
            "netlist_name": "001_02_0.txt",
            "current_mirror_name": "current_mirror_2",
            "testbench_description": "Testbench for AC impedance analysis of current_mirror_2 (10kHz to 10MHz)",
            "testbench_name": "current_mirror_2_impedance_test.scs",
            "ac_analysis_settings": {
                "start_freq": 10000.0,
                "stop_freq": 10000000.0,
                "steps": 3,
                "step_type": "dec",
            },
            "noise_analysis_settings": {
                "start_freq": 1000.0,
                "stop_freq": 10000000.0,
                "steps": 10,
                "step_type": "dec",
            },
            "voltage_source_settings": {
                "power_supply_voltage": 1.8,
                "bias_current": 1e-5,
                "primary_cascode_dc_bias": 0.8,
                "primary_cascode_ac_stimulus": 1.0,
                "secondary_voltage_source_dc": 0.5,
                "secondary_voltage_source_ac": 1.0,
            },
            "analysis_types": {"ac_analysis": True, "noise_analysis": False},
        },
        "id": "chatcmpl-tool-924103cb3ed2478990fbd41d341355e6",
        "type": "tool_call",
    }

    # Compare JSONs
    diffs = fastjsondiff.compare_json(
        json1,
        json2,
        allow=[
            "args/netlist_name",
            "args/current_mirror_name",
        ],
    )
    print("Differences found:", diffs)

    # # Test with ignore
    # diffs_ignore = fastjsondiff.compare_json(json1, json2, ignore=["b"])
    # print("Differences with ignore:", diffs_ignore)

    # # Test with allow
    # diffs_allow = fastjsondiff.compare_json(json1, json2, allow=["c"])
    # print("Differences with allow:", diffs_allow)


if __name__ == "__main__":
    test_basic_comparison()
