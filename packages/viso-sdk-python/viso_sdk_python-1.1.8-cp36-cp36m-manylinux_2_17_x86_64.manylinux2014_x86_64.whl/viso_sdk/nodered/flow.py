"""
Wrapper for the Flow API. This module is normally used to parse flow information from the Node-RED.
"""

import time
import requests
from typing import Optional, Union

from viso_sdk.constants import Module, NODE_ID, NODE_TYPE
from viso_sdk.logging import get_logger

logger = get_logger(name="FLOW")


class FlowAPIWrapper:
    """Represents a Viso flow related API instance

    Args:
        host(str): Host of the Node-RED server.  Normally 127.0.0.1
        port(int): Port of the Node-RED server.  Default value is 1880
        node_id(str): ID of the node.           Use NODE_ID env var if not set.
        node_type(str): Type of the node.       Use NODE_TYPE env var if not set.
    """

    def __init__(
            self,
            host: Optional[str] = "127.0.0.1",
            port: Optional[int] = 1880,
            node_id: Optional[str] = "",
            node_type: Optional[str] = "",
    ) -> None:

        self.url: str = f"http://{host}:{port}"
        self._nodes: dict = {}
        self._visited_node_ids: list = []
        self.node_id = node_id or NODE_ID
        self.node_type = node_type or NODE_TYPE

    def _load_flow(self, timeout: int = 5 * 60) -> bool:
        """
        Pull flow from Node-RED server and compose a dict

        Args:
            timeout(int): Timeout value in seconds. Default is 5 minutes.
        """
        s_t = time.time()
        while True:
            try:
                resp = requests.get(
                    f"{self.url}/flows", headers={"Node-RED-API-Version": "v2"}
                )
                flows = resp.json().get("flows")
                break
            except Exception as err:
                logger.error(f"Failed to parse flow - {err}")

            if time.time() - s_t > timeout:
                logger.error(f"Failed to download flow in {timeout} sec, exiting...")
                return False
            time.sleep(1)

        self._nodes = {f["id"]: f for f in flows}
        return True

    def parse_flow(self) -> Union[dict, None]:
        """Parse node-RED flow to find current/previous/next/vid-fed nodes

        Returns:
            dict: The result of the current, previous, next, and video-feed node.

                .. code-block:: python

                    {
                        "cur_node": current node(dict)
                        "prev_nodes": list of previous nodes
                        "next_nodes": list of next nodes
                        "vid_fed": {"flow": video feed node, "port": video port id}
                    }
        """
        self._visited_node_ids = []

        if not self._load_flow():
            return None

        # current_node
        if self._nodes[self.node_id]["type"] == self.node_type:
            cur_node = self._nodes[self.node_id]
        else:
            logger.error(
                f"Could not to find node({self.node_type}) with id({self.node_id}), exiting..."
            )
            return None
        logger.info(f"Node info: {cur_node}")
        # Seek previous nodes
        prev_nodes = self.seek_prev_nodes(cur_node)
        logger.info(f"Previous nodes - {prev_nodes}")

        # Seek next nodes
        next_nodes = self.seek_next_nodes(cur_node)
        logger.info(f"Next nodes - {next_nodes}")

        vid_feed, vid_port_id = self.seek_video_feed(cur_node)
        logger.info(f"vid-fed node - {vid_feed}, {vid_port_id}")

        return dict(
            cur_node=cur_node,
            prev_nodes=prev_nodes,
            next_nodes=next_nodes,
            vid_fed={"flow": vid_feed, "port": vid_port_id},
        )

    def seek_prev_nodes(self, cur_node: dict) -> list:
        """Seek previous nodes that have the target node as a child.

        Args:
            cur_node(dict): Target node info
        """
        prev_nodes = []
        for node in self._nodes.values():
            for idx, next_node_id in enumerate(node.get("wires", [])):
                if cur_node.get("id") in next_node_id:
                    prev_nodes.append({
                        "node": node,
                        "port": idx
                    })
        return prev_nodes

    def seek_next_nodes(self, cur_node: dict) -> list:
        """Seek next nodes that have the target node as a parent.

        Args:
            cur_node(dict): Target node info
        """
        next_nodes = []
        for idx, next_node_ids in enumerate(cur_node.get("wires", [])):
            for wired_node_id in next_node_ids:
                # next_nodes.append([self._nodes[wired_node_id], idx])
                next_nodes.append({
                    "node": self._nodes[wired_node_id],
                    "port": idx
                })
        return next_nodes

    def seek_video_feed(self, cur_node: dict) -> tuple:
        """Seek VidFed node that has the target node as a child.

        Args:
            cur_node(dict): Target node info
        """
        vid_feed_node, vid_feed_port_id = None, None
        prevs = self.seek_prev_nodes(cur_node)
        self._visited_node_ids.append(cur_node["id"])

        for prev in prevs:
            prev_n, prev_port_id = prev['node'], prev['port']
            if prev_n["type"] in [Module.VideoFeed.type, Module.VFVideoFile.type, Module.VFUsbCamera.type,
                                  Module.VFIpCamera.type]:
                return prev_n, prev_port_id
            if len(self.seek_prev_nodes(prev_n)) == 0:
                continue
            if prev_n["id"] in self._visited_node_ids:
                continue
            vid_feed_node, vid_feed_port_id = self.seek_video_feed(prev_n)
            if vid_feed_node is not None:
                break
        return vid_feed_node, vid_feed_port_id
