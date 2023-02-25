test_compose_string = """
version: "3.9"
services:
  example:
    image: "busybox"
    container_name: example_container
    command: [
      "echo",
      "Hello again, with a different message."
    ]
  example-config:
    image: "busybox"
    container_name: example_container_config
    command: [
      "cat",
      "/dev/config.json"
    ]
    volumes:
      - type: bind
        source: "./test.configmap"
        target: "/dev/config.json\"
"""

test_details = {
    'name': 'test-application',
    'version': '1.0.0',
    'alwaysPull': True,
    'guid': '152899af-1ebd-4969-94cc-d576c81e625a',
    'timestamp': 1677333827.9829454,
    'compose_name': '/home/sam/PycharmProjects/composition/examples/basic_application/template.yaml'
}