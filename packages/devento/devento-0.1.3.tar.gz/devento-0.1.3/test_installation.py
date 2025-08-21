#!/usr/bin/env python3
"""
Test script to verify Devento SDK installation.

Run this script to ensure the Devento SDK is properly installed and functional.
"""

import sys


def test_installation():
    """Test that the Devento SDK is properly installed."""
    print("🧪 Testing Devento SDK Installation")
    print("=" * 40)

    try:
        # Test basic imports
        print("1. Testing imports...")
        import devento

        print(f"   ✓ Devento SDK version: {devento.__version__}")

        # Test core classes
        from devento import (
            Devento,
            BoxConfig,
            BoxStatus,
            CommandResult,
            CommandStatus,
            DeventoError,
        )

        print("   ✓ Core classes imported successfully")

        # Test async classes if available
        try:
            from devento import AsyncDevento, AsyncBoxHandle

            print("   ✓ Async classes imported successfully")
            async_available = True
        except ImportError:
            print(
                "   ⚠ Async classes not available (install with: pip install devento[async])"
            )
            async_available = False

        # Test client initialization
        print("\n2. Testing client initialization...")
        try:
            client = Devento(api_key="test-key")
            print("   ✓ Sync client initialized")
        except Exception as e:
            print(f"   ✗ Sync client failed: {e}")
            return False

        if async_available:
            try:
                import asyncio

                async def test_async():
                    async with AsyncDevento(api_key="test-key") as client:
                        return True

                asyncio.run(test_async())
                print("   ✓ Async client initialized")
            except Exception as e:
                print(f"   ✗ Async client failed: {e}")

        # Test configuration
        print("\n3. Testing configuration...")
        config = BoxConfig(
            template=BoxTemplate.PRO, timeout=3600, metadata={"test": "installation"}
        )
        print("   ✓ BoxConfig created successfully")

        # Test enum values
        print("\n4. Testing enums...")
        assert BoxStatus.RUNNING == "running"
        assert CommandStatus.DONE == "done"
        assert BoxTemplate.BASIC == "Basic"
        assert BoxTemplate.PRO == "Pro"
        print("   ✓ Enum values correct")

        # Test exception handling
        print("\n5. Testing exceptions...")
        try:
            raise DeventoError("Test error")
        except DeventoError:
            print("   ✓ Exception handling works")

        print("\n" + "=" * 40)
        print("🎉 All tests passed! Devento SDK is ready to use.")
        print("\nTo get started:")
        print("1. Get your API key from https://devento.ai")
        print("2. Replace 'your-api-key' in your code")
        print("3. Start creating boxes!")

        return True

    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("\nPlease install the Devento SDK:")
        print("  pip install devento")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = test_installation()
    sys.exit(0 if success else 1)
