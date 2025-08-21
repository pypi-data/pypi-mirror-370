#!/usr/bin/env python3
"""Test SSE streaming implementation."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from devento import Devento, BoxConfig


def test_streaming():
    print("Testing SSE streaming implementation...\n")
    
    # Initialize client
    devento = Devento(
        api_key=os.environ.get("DEVENTO_API_KEY"),
        base_url=os.environ.get("DEVENTO_BASE_URL", "https://api.devento.ai")
    )
    
    try:
        with devento.box(BoxConfig(cpu=1, mib_ram=1024)) as box:
            print(f"Box {box.id} is ready!\n")
            
            # Test 1: Basic streaming
            print("Test 1: Basic streaming output")
            print("==============================")
            
            result = box.run(
                'for i in {1..3}; do echo "Line $i"; sleep 0.5; done',
                on_stdout=lambda line: print(f"[STDOUT] {line}"),
                on_stderr=lambda line: print(f"[STDERR] {line}")
            )
            
            print(f"\nTest 1 completed! Exit code: {result.exit_code}\n")
            
            # Test 2: Mixed stdout/stderr
            print("Test 2: Mixed stdout and stderr")
            print("================================")
            
            result = box.run(
                'echo "This is stdout"; >&2 echo "This is stderr"; echo "More stdout"',
                on_stdout=lambda line: print(f"[OUT] {line}"),
                on_stderr=lambda line: print(f"[ERR] {line}")
            )
            
            print(f"\nTest 2 completed! Exit code: {result.exit_code}\n")
            
            # Test 3: Without streaming (should use polling)
            print("Test 3: Non-streaming execution")
            print("================================")
            
            result = box.run('echo "Hello from non-streaming"')
            print(f"Result stdout: {result.stdout.strip()}")
            print(f"Result stderr: {result.stderr.strip()}")
            print(f"Exit code: {result.exit_code}")
            
            print("\nAll tests completed successfully!")
            
    except Exception as e:
        print(f"Test failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    test_streaming()