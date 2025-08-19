# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2023 viso.ai AG <info@viso.ai>
"""
Testing module for the flow
"""
import json

import pytest
import responses
from responses import matchers

from viso_sdk.nodered import VisoFlow


@pytest.fixture()
def json_content(fixture_dir):
    with open(fixture_dir / "flow.json", "r", encoding="utf-8") as f:
        todo_content = f.read()
        return json.loads(todo_content)


@pytest.fixture
def resp_get_flow(json_content):
    with responses.RequestsMock() as rsps:
        rsps.add(
            method=responses.GET,
            url="http://127.0.0.1:1880/flows",
            content_type="application/json",
            match=[matchers.header_matcher({"Node-RED-API-Version": "v2"})],
            json=json_content,
            status=200,
        )
        yield rsps


@pytest.fixture
def flow_obj_det():
    return VisoFlow(node_id="638acaf9.bf6014", node_type="object-detection")


def test_parse_flow(flow_obj_det: VisoFlow, resp_get_flow):
    result = flow_obj_det.parse_flow()
    assert result["cur_node"]["devices"] == "CPU"
    assert result["cur_node"]["framework"] == "openvino"
    assert result["prev_nodes"][0][0]["type"] == "region-of-interest"
    assert result["next_nodes"][0][0]["type"] == "video-view"
    assert result["vid_fed"]["port_id"] == 1
    assert result["vid_fed"]["flow"]["type"] == "video-feed"
    assert result["vid_fed"]["flow"]["video_source_info"][0]["video_type"] == "file"
