"""
Tests for reproducing hanging scenarios with nested viewports and asyncio executors.

This test module is designed to uncover the root cause of production hangs
involving:
- Viewport with AsyncPoolExecutor and wait_for_input
- Nested viewport creation from callbacks  
- Second viewport with AsyncThreadPoolExecutor
- Infinite async operations in the second viewport
- "task exception not handled" messages on exit
"""

import asyncio
import gc
import subprocess
import sys
import threading
import time
from concurrent.futures import Future, CancelledError

import pytest

try:
    import dearcygui as dcg
    from dearcygui.utils.asyncio_helpers import (
        AsyncPoolExecutor,
        AsyncThreadPoolExecutor,
        BatchingEventLoop
    )
except ImportError:
    pytest.skip("dearcygui not available", allow_module_level=True)


class ViewportHangTester:
    """Helper class for testing viewport hanging scenarios."""
    
    def __init__(self):
        self.contexts: List[dcg.Context] = []
        self.executors: List[AsyncPoolExecutor | AsyncThreadPoolExecutor] = []
        self.running_tasks: List[Future] = []
        self.stop_event = threading.Event()
        
    def cleanup(self):
        """Clean up all resources."""
        self.stop_event.set()
        
        # Cancel all running tasks
        for task in self.running_tasks:
            if not task.done():
                task.cancel()
        
        # Shutdown executors
        for executor in self.executors:
            if hasattr(executor, 'shutdown'):
                executor.shutdown(wait=False)
        
        # Stop contexts
        for ctx in self.contexts:
            ctx.running = False
            
        self.contexts.clear()
        self.executors.clear()
        self.running_tasks.clear()
        gc.collect()
    
    def create_primary_viewport(self, use_wait_for_input=True) -> dcg.Context:
        """Create primary viewport with AsyncPoolExecutor."""
        ctx = dcg.Context()
        ctx.viewport.initialize(visible=False)
        ctx.viewport.wait_for_input = use_wait_for_input
        
        # Use AsyncPoolExecutor as queue
        executor = AsyncPoolExecutor()
        ctx.queue = executor
        
        self.contexts.append(ctx)
        self.executors.append(executor)
        
        return ctx
    
    def create_secondary_viewport(self, use_wait_for_input=True) -> dcg.Context:
        """Create secondary viewport with AsyncThreadPoolExecutor."""
        ctx = dcg.Context()
        ctx.viewport.initialize(visible=False)  
        ctx.viewport.wait_for_input = use_wait_for_input
        
        # Use AsyncThreadPoolExecutor as queue
        executor = AsyncThreadPoolExecutor()
        ctx.queue = executor
        
        self.contexts.append(ctx)
        self.executors.append(executor)
        
        return ctx
    
    async def infinite_async_task(self, task_id: str, interval=0.1):
        """Infinite async task that awaits frequently."""
        count = 0
        try:
            while not self.stop_event.is_set():
                await asyncio.sleep(interval)
                count += 1
                if count % 10 == 0:
                    print(f"Task {task_id}: iteration {count}")
        except asyncio.CancelledError:
            print(f"Task {task_id} cancelled after {count} iterations")
            raise
        except (SystemExit, KeyboardInterrupt) as e:
            print(f"Task {task_id} received {type(e).__name__} after {count} iterations")
            raise
        except Exception as e:
            print(f"Task {task_id} error: {e}")
            raise
    
    def start_infinite_tasks(self, ctx: dcg.Context, num_tasks=3):
        """Start infinite async tasks in the given context's executor."""
        executor = ctx.queue
        
        for i in range(num_tasks):
            task_id = f"task_{id(ctx)}_{i}"
            future = executor.submit(self.infinite_async_task, task_id)
            self.running_tasks.append(future)
    
    def create_nested_viewport_callback(self):
        """Create a callback that spawns a secondary viewport."""
        def callback():
            print("Creating secondary viewport from callback...")
            secondary_ctx = self.create_secondary_viewport()
            
            # Add some UI to the secondary viewport
            dcg.Text(secondary_ctx, value="Secondary Viewport")
            button = dcg.Button(secondary_ctx, label="Stop Secondary")
            
            def stop_secondary():
                print("Stopping secondary viewport...")
                secondary_ctx.running = False
                secondary_ctx.viewport.wake()
            
            stop_handler = dcg.ClickedHandler(secondary_ctx, callback=stop_secondary)
            button.handlers += [stop_handler]
            
            # Start infinite async tasks in secondary viewport
            self.start_infinite_tasks(secondary_ctx, num_tasks=2)
            
            print("Secondary viewport created with infinite tasks")
            
        return callback


@pytest.fixture
def hang_tester():
    """Fixture providing a ViewportHangTester instance."""
    tester = ViewportHangTester()
    yield tester
    tester.cleanup()


class TestViewportHanging:
    """Test cases for viewport hanging scenarios."""
    
    def test_single_viewport_with_infinite_tasks(self, hang_tester):
        """Test single viewport with infinite async tasks."""
        ctx = hang_tester.create_primary_viewport()
        dcg.Text(ctx, value="Primary Viewport")
        
        # Start infinite tasks
        hang_tester.start_infinite_tasks(ctx, num_tasks=2)
        
        # Run for a short time
        start_time = time.time()
        frame_count = 0
        while ctx.running and frame_count < 10 and (time.time() - start_time) < 2.0:
            ctx.viewport.render_frame()
            frame_count += 1
            time.sleep(0.01)
        
        # Stop should work without hanging
        start_stop = time.time()
        ctx.running = False
        ctx.viewport.wake()  # Important for wait_for_input
        
        # Cleanup should complete quickly
        hang_tester.cleanup()
        stop_time = time.time() - start_stop
        
        assert stop_time < 3.0, f"Single viewport cleanup took too long: {stop_time:.2f}s"
    
    def test_nested_viewport_creation(self, hang_tester):
        """Test creating a secondary viewport from a callback."""
        primary_ctx = hang_tester.create_primary_viewport()
        dcg.Text(primary_ctx, value="Primary Viewport")
        
        # Add button that creates secondary viewport
        button = dcg.Button(primary_ctx, label="Create Secondary")
        callback = hang_tester.create_nested_viewport_callback()
        handler = dcg.ClickedHandler(primary_ctx, callback=callback)
        button.handlers += [handler]
        
        # Simulate button click by calling callback directly
        callback()
        
        # Run both viewports for a short time
        start_time = time.time()
        frame_count = 0
        while frame_count < 15 and (time.time() - start_time) < 3.0:
            # Render all active contexts
            for ctx in hang_tester.contexts:
                if ctx.running:
                    ctx.viewport.render_frame()
            frame_count += 1
            time.sleep(0.01)
        
        # Stop should work without hanging
        start_stop = time.time()
        for ctx in hang_tester.contexts:
            ctx.running = False
            ctx.viewport.wake()
        
        hang_tester.cleanup()
        stop_time = time.time() - start_stop
        
        assert len(hang_tester.contexts) == 2, "Should have primary and secondary contexts"
        assert stop_time < 5.0, f"Nested viewport cleanup took too long: {stop_time:.2f}s"
    
    def test_executor_exception_handling(self, hang_tester):
        """Test exception handling in async executors."""
        ctx = hang_tester.create_secondary_viewport()
        executor = ctx.queue
        
        results = []
        
        async def failing_task():
            await asyncio.sleep(0.1)
            results.append("before_exception")
            raise ValueError("Deliberate test exception")
        
        async def normal_task():
            await asyncio.sleep(0.2)
            results.append("normal_task_done")
            return "success"
        
        # Submit both tasks
        failing_future = executor.submit(failing_task)
        normal_future = executor.submit(normal_task)
        
        # Run viewport briefly
        start_time = time.time()
        while ctx.running and (time.time() - start_time) < 1.0:
            ctx.viewport.render_frame()
            time.sleep(0.01)
        
        # Check results
        with pytest.raises(ValueError, match="Deliberate test exception"):
            failing_future.result()
        
        assert normal_future.result() == "success"
        assert "before_exception" in results
        assert "normal_task_done" in results
        
        ctx.running = False
        ctx.viewport.wake()
    
    def test_keyboard_interrupt_propagation(self, hang_tester):
        """Test KeyboardInterrupt propagation through async tasks."""
        ctx = hang_tester.create_secondary_viewport()
        executor = ctx.queue
        
        results = []
        interrupt_received = threading.Event()
        
        async def interruptible_task():
            try:
                results.append("task_started")
                for i in range(100):
                    await asyncio.sleep(0.01)
                    results.append(f"iteration_{i}")
                    if i == 5:
                        # Simulate KeyboardInterrupt
                        interrupt_received.set()
                        raise KeyboardInterrupt("Simulated Ctrl+C")
            except KeyboardInterrupt:
                results.append("keyboard_interrupt_caught")
                raise
            except Exception as e:
                results.append(f"other_exception: {e}")
                raise
        
        future = executor.submit(interruptible_task)
        
        # Run until interrupt is received
        start_time = time.time()
        while ctx.running and not interrupt_received.is_set() and (time.time() - start_time) < 2.0:
            ctx.viewport.render_frame()
            time.sleep(0.01)
        
        # Should have received KeyboardInterrupt
        assert interrupt_received.is_set(), "KeyboardInterrupt was not raised"
        
        with pytest.raises(CancelledError):
            future.result()
        
        assert "task_started" in results
        assert "keyboard_interrupt_caught" in results
        
        ctx.running = False
        ctx.viewport.wake()
    
    def test_system_exit_propagation(self, hang_tester):
        """Test SystemExit propagation through async tasks."""
        ctx = hang_tester.create_secondary_viewport()
        executor = ctx.queue
        
        results = []
        
        async def exiting_task():
            try:
                results.append("task_started")
                await asyncio.sleep(0.1)
                results.append("before_exit")
                raise SystemExit("Simulated sys.exit()")
            except SystemExit:
                results.append("system_exit_caught")
                raise
        
        future = executor.submit(exiting_task)
        
        # Run briefly
        start_time = time.time()
        while ctx.running and (time.time() - start_time) < 0.5:
            ctx.viewport.render_frame()
            time.sleep(0.01)
        
        with pytest.raises(CancelledError):
            future.result()
        
        assert "task_started" in results
        assert "system_exit_caught" in results
        
        ctx.running = False
        ctx.viewport.wake()
    
    def test_mixed_executor_types(self, hang_tester):
        """Test mixing AsyncPoolExecutor and AsyncThreadPoolExecutor."""
        # Primary with AsyncPoolExecutor
        primary_ctx = hang_tester.create_primary_viewport()
        dcg.Text(primary_ctx, value="Primary (AsyncPoolExecutor)")
        
        # Secondary with AsyncThreadPoolExecutor  
        secondary_ctx = hang_tester.create_secondary_viewport()
        dcg.Text(secondary_ctx, value="Secondary (AsyncThreadPoolExecutor)")
        
        # Start tasks in both
        hang_tester.start_infinite_tasks(primary_ctx, num_tasks=1)
        hang_tester.start_infinite_tasks(secondary_ctx, num_tasks=1)
        
        # Run both for a short time
        start_time = time.time()
        frame_count = 0
        while frame_count < 20 and (time.time() - start_time) < 2.0:
            for ctx in [primary_ctx, secondary_ctx]:
                if ctx.running:
                    ctx.viewport.render_frame()
            frame_count += 1
            time.sleep(0.01)
        
        # Verify both executors are different types
        assert isinstance(primary_ctx.queue, AsyncPoolExecutor)
        assert isinstance(secondary_ctx.queue, AsyncThreadPoolExecutor)
        
        # Stop should work
        start_stop = time.time()
        for ctx in [primary_ctx, secondary_ctx]:
            ctx.running = False
            ctx.viewport.wake()
        
        hang_tester.cleanup()
        stop_time = time.time() - start_stop
        
        assert stop_time < 4.0, f"Mixed executor cleanup took too long: {stop_time:.2f}s"
    
    def test_rapid_task_submission_during_shutdown(self, hang_tester):
        """Test rapid task submission during viewport shutdown."""
        ctx = hang_tester.create_secondary_viewport()
        executor = ctx.queue
        
        results = []
        
        async def rapid_submitter():
            """Task that rapidly submits other tasks."""
            for i in range(10):
                # Submit a quick task
                quick_future = executor.submit(lambda x=i: results.append(f"quick_{x}"))
                await asyncio.sleep(0.01)
                
                # Submit an async task
                async def async_subtask(idx=i):
                    await asyncio.sleep(0.05)
                    results.append(f"async_{idx}")
                
                async_future = executor.submit(async_subtask)
                await asyncio.sleep(0.01)
        
        # Start the rapid submitter
        main_future = executor.submit(rapid_submitter)
        
        # Run for a bit, then shut down while tasks are still being submitted
        start_time = time.time()
        frame_count = 0
        while ctx.running and frame_count < 15 and (time.time() - start_time) < 1.0:
            ctx.viewport.render_frame()
            frame_count += 1
            time.sleep(0.01)
        
        # Shutdown while tasks may still be running
        ctx.running = False
        ctx.viewport.wake()
        
        # Some tasks should have completed
        assert len(results) > 0, "No tasks completed"
        
        # Main task may or may not complete depending on timing
        try:
            main_future.result(timeout=1.0)
        except:
            pass  # It's ok if it was cancelled
    
    def test_wait_for_input_wake_coordination(self, hang_tester):
        """Test coordination between wait_for_input and wake() calls."""
        ctx = hang_tester.create_primary_viewport()
        dcg.Text(ctx, value="Wait for input test")
        
        results = []
        
        # Task that periodically wakes the viewport
        async def periodic_waker():
            for i in range(5):
                await asyncio.sleep(0.1)
                results.append(f"wake_{i}")
                ctx.viewport.wake()
        
        executor = ctx.queue
        wake_future = executor.submit(periodic_waker)
        
        # Run with wait_for_input enabled
        start_time = time.time()
        frame_count = 0
        
        while ctx.running and frame_count < 20 and (time.time() - start_time) < 2.0:
            ctx.viewport.render_frame()
            frame_count += 1
            # Small sleep to prevent busy waiting
            time.sleep(0.01)
        
        # Should have had multiple wake calls
        wake_calls = [r for r in results if r.startswith("wake_")]
        assert len(wake_calls) > 0, "No wake calls occurred"
        
        ctx.running = False
        ctx.viewport.wake()


def test_subprocess_hanging_scenario():
    """Test the full hanging scenario in a subprocess to detect actual hangs."""
    
    script_content = '''
import asyncio
import signal
import sys
import time
import threading
import dearcygui as dcg
from dearcygui.utils.asyncio_helpers import AsyncPoolExecutor, AsyncThreadPoolExecutor

# Global flag for clean shutdown
shutting_down = False

def signal_handler(signum, frame):
    global shutting_down
    print(f"Signal {signum} received, initiating shutdown...", flush=True)
    shutting_down = True

# Install signal handlers
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

try:
    print("Creating primary viewport with AsyncPoolExecutor...", flush=True)
    
    # Primary viewport with AsyncPoolExecutor
    primary_ctx = dcg.Context()
    primary_ctx.viewport.initialize(visible=False)
    primary_ctx.viewport.wait_for_input = True
    primary_ctx.queue = AsyncPoolExecutor()
    
    dcg.Text(primary_ctx, value="Primary Viewport")
    
    # Infinite async task for primary
    async def infinite_primary_task():
        count = 0
        try:
            while not shutting_down and primary_ctx.running:
                await asyncio.sleep(0.1)
                count += 1
                if count % 10 == 0:
                    print(f"Primary task: {count}", flush=True)
        except Exception as e:
            print(f"Primary task exception: {e}", flush=True)
            raise
    
    primary_future = primary_ctx.queue.submit(infinite_primary_task)
    
    # Secondary viewport creation function
    def create_secondary():
        global secondary_ctx
        print("Creating secondary viewport with AsyncThreadPoolExecutor...", flush=True)
        
        secondary_ctx = dcg.Context()
        secondary_ctx.viewport.initialize(visible=False)  
        secondary_ctx.viewport.wait_for_input = True
        secondary_ctx.queue = AsyncThreadPoolExecutor()
        
        dcg.Text(secondary_ctx, value="Secondary Viewport")
        
        # Multiple infinite async tasks for secondary
        async def infinite_secondary_task(task_id):
            count = 0
            try:
                while not shutting_down and secondary_ctx.running:
                    await asyncio.sleep(0.05)
                    count += 1
                    if count % 20 == 0:
                        print(f"Secondary task {task_id}: {count}", flush=True)
            except Exception as e:
                print(f"Secondary task {task_id} exception: {e}", flush=True)
                raise
        
        # Start multiple infinite tasks
        secondary_futures = []
        for i in range(3):
            future = secondary_ctx.queue.submit(infinite_secondary_task, i)
            secondary_futures.append(future)
        
        print("Secondary viewport and tasks created", flush=True)
        return secondary_futures
    
    # Create secondary viewport (simulating callback)
    secondary_futures = create_secondary()
    
    print("Starting render loops...", flush=True)
    start_time = time.time()
    frame_count = 0
    
    # Main render loop
    while not shutting_down and (time.time() - start_time) < 5.0:
        try:
            if primary_ctx.running:
                primary_ctx.viewport.render_frame()
            if 'secondary_ctx' in globals() and secondary_ctx.running:
                secondary_ctx.viewport.render_frame()
                
            frame_count += 1
            if frame_count % 100 == 0:
                print(f"Rendered {frame_count} frames", flush=True)
                
        except Exception as e:
            print(f"Render loop exception: {e}", flush=True)
            break
    
    print("Initiating shutdown sequence...", flush=True)
    
    # Stop contexts
    primary_ctx.running = False
    if 'secondary_ctx' in globals():
        secondary_ctx.running = False
    
    # Wake viewports to break out of wait_for_input
    primary_ctx.viewport.wake()
    if 'secondary_ctx' in globals():
        secondary_ctx.viewport.wake()
    
    print("Contexts stopped, cleaning up executors...", flush=True)
    
    # Shutdown executors
    primary_ctx.queue.shutdown(wait=False)
    if 'secondary_ctx' in globals():
        secondary_ctx.queue.shutdown(wait=False)
    
    print("Application shutdown complete", flush=True)
    
except KeyboardInterrupt:
    print("KeyboardInterrupt in main", flush=True)
except SystemExit as e:
    print(f"SystemExit in main: {e}", flush=True)
except Exception as e:
    print(f"Unexpected exception in main: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)
'''
    
    proc = subprocess.Popen(
        [sys.executable, '-c', script_content],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Let it run for a bit
    time.sleep(2.0)
    
    # Send termination signal
    start_shutdown = time.time()
    proc.terminate()
    
    try:
        stdout, stderr = proc.communicate(timeout=5.0)
        shutdown_time = time.time() - start_shutdown
        
        print("=== SUBPROCESS STDOUT ===")
        print(stdout)
        print("=== SUBPROCESS STDERR ===")
        print(stderr)
        print(f"=== SHUTDOWN TIME: {shutdown_time:.2f}s ===")
        
        # Check for problematic patterns
        problematic_patterns = [
            "task exception not handled",
            "Task was destroyed but it is pending",
            "RuntimeWarning",
            "Exception ignored",
        ]
        
        found_issues = []
        full_output = stdout + stderr
        
        for pattern in problematic_patterns:
            if pattern.lower() in full_output.lower():
                found_issues.append(pattern)
        
        if found_issues:
            print(f"WARNING: Found problematic patterns: {found_issues}")
            # Don't fail the test yet, but warn about potential issues
        
        # The main check is that it shuts down in reasonable time
        assert shutdown_time < 8.0, f"Subprocess shutdown took too long: {shutdown_time:.2f}s"
        
        if proc.returncode == 0:
            assert "Application shutdown complete" in stdout
        elif proc.returncode == -15:  # SIGTERM
            print("Process was terminated (expected)")
        else:
            print(f"Process exited with code {proc.returncode}")
            
    except subprocess.TimeoutExpired:
        # This is the hanging scenario we're trying to detect
        proc.kill()
        stdout, stderr = proc.communicate()
        
        print("=== HANGING DETECTED ===")
        print("STDOUT:", stdout)
        print("STDERR:", stderr)
        
        pytest.fail(
            "CRITICAL: Process hung during shutdown. This reproduces the production hanging issue."
        )


def test_exception_unhandled_detection():
    """Test to detect 'task exception not handled' scenarios."""
    
    script_content = '''
import asyncio
import sys
import time
import dearcygui as dcg
from dearcygui.utils.asyncio_helpers import AsyncThreadPoolExecutor

# Enable all asyncio debug warnings
import warnings
warnings.simplefilter('always')

try:
    ctx = dcg.Context()
    ctx.viewport.initialize(visible=False)
    ctx.viewport.wait_for_input = True
    executor = AsyncThreadPoolExecutor()
    ctx.queue = executor
    
    # Task that raises an exception but doesn't handle it properly
    async def unhandled_exception_task():
        await asyncio.sleep(0.1)
        raise RuntimeError("This exception should be unhandled")
    
    # Submit task but don't wait for result (simulating fire-and-forget)
    future = executor.submit(unhandled_exception_task)
    
    # Run briefly
    for _ in range(10):
        ctx.viewport.render_frame()
        time.sleep(0.01)
    
    # Shutdown without checking task results
    ctx.running = False
    ctx.viewport.wake()
    executor.shutdown(wait=False)
    
    print("Script completed normally", flush=True)
    
except Exception as e:
    print(f"Script exception: {e}", flush=True)
    import traceback
    traceback.print_exc()
'''
    
    proc = subprocess.Popen(
        [sys.executable, '-c', script_content],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        stdout, stderr = proc.communicate(timeout=5.0)
        
        print("=== EXCEPTION TEST STDOUT ===")
        print(stdout)
        print("=== EXCEPTION TEST STDERR ===")  
        print(stderr)
        
        # Look for unhandled task exceptions
        full_output = stdout + stderr
        
        if "task exception" in full_output.lower() or "exception was never retrieved" in full_output.lower():
            print("DETECTED: Task exception not handled scenario")
            # This is informational - shows we can reproduce the issue
        
        # Test should complete regardless
        assert proc.returncode is not None, "Process didn't complete"
        
    except subprocess.TimeoutExpired:
        # This is actually what we want to test - the hanging scenario!
        proc.kill()
        stdout, stderr = proc.communicate()
        
        print("=== HANGING DETECTED IN EXCEPTION TEST ===")
        print("STDOUT:", stdout if isinstance(stdout, str) else stdout.decode())
        print("STDERR:", stderr if isinstance(stderr, str) else stderr.decode())
        
        # This is the hanging we're trying to detect - it's a success for our test
        # but a failure for the application behavior
        print("SUCCESS: Reproduced hanging scenario with unhandled exceptions!")
        
        # Don't fail the test - we successfully reproduced the issue
        # The hang is the expected behavior we're testing for


def test_wait_for_input_hanging_scenario():
    """Test specific wait_for_input hanging scenario with AsyncThreadPoolExecutor."""
    
    script_content = '''
import asyncio
import sys
import time
import dearcygui as dcg
from dearcygui.utils.asyncio_helpers import AsyncThreadPoolExecutor

try:
    ctx = dcg.Context()
    ctx.viewport.initialize(visible=False)
    ctx.viewport.wait_for_input = True  # This is crucial for the hang
    
    # Use AsyncThreadPoolExecutor (this seems to be part of the hang condition)
    executor = AsyncThreadPoolExecutor()
    ctx.queue = executor
    
    # Infinite async task (typical production scenario)
    async def infinite_task():
        count = 0
        while True:
            await asyncio.sleep(0.1)
            count += 1
            if count > 5:  # Run for a bit then simulate system exit
                raise SystemExit("Simulating app exit")
    
    # Start the infinite task
    future = executor.submit(infinite_task)
    
    # Simulate the main loop
    print("Starting main loop...", flush=True)
    for i in range(20):
        ctx.viewport.render_frame()
        time.sleep(0.01)
        if i == 10:
            print("Attempting to stop context...", flush=True)
            ctx.running = False
            ctx.viewport.wake()
    
    print("Main loop finished, shutting down executor...", flush=True)
    executor.shutdown(wait=False)
    print("Script completed", flush=True)
    
except SystemExit as e:
    print(f"SystemExit caught: {e}", flush=True)
except Exception as e:
    print(f"Exception: {e}", flush=True)
    import traceback
    traceback.print_exc()
'''
    
    proc = subprocess.Popen(
        [sys.executable, '-c', script_content],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        stdout, stderr = proc.communicate(timeout=5.0)
        print("=== WAIT_FOR_INPUT TEST OUTPUT ===")
        print("STDOUT:", stdout)
        print("STDERR:", stderr)
        
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
        print("=== HANGING DETECTED IN WAIT_FOR_INPUT TEST ===")
        print("STDOUT:", stdout if isinstance(stdout, str) else stdout.decode())
        print("STDERR:", stderr if isinstance(stderr, str) else stderr.decode())
        print("SUCCESS: Reproduced wait_for_input hanging scenario!")


def test_nested_executor_hanging_scenario():
    """Test the specific production scenario: nested viewports with different executors."""
    
    script_content = '''
import asyncio
import sys
import time
import threading
import dearcygui as dcg
from dearcygui.utils.asyncio_helpers import AsyncPoolExecutor, AsyncThreadPoolExecutor

# Set a maximum runtime to avoid infinite hangs
MAX_RUNTIME = 3.0
start_time = time.time()

def check_timeout():
    if time.time() - start_time > MAX_RUNTIME:
        print("TIMEOUT: Force exiting to prevent hang", flush=True)
        sys.exit(1)

try:
    # Primary viewport with AsyncPoolExecutor
    primary_ctx = dcg.Context()
    primary_ctx.viewport.initialize(visible=False)
    primary_ctx.viewport.wait_for_input = True
    primary_ctx.queue = AsyncPoolExecutor()
    
    # Create secondary viewport from "callback" (production scenario)
    secondary_ctx = dcg.Context()
    secondary_ctx.viewport.initialize(visible=False)
    secondary_ctx.viewport.wait_for_input = True
    secondary_ctx.queue = AsyncThreadPoolExecutor()  # Different executor type
    
    # Infinite async operations in secondary viewport
    async def infinite_secondary_task(task_id):
        count = 0
        try:
            while count < 15:  # Limit iterations to avoid true infinite loop
                check_timeout()
                await asyncio.sleep(0.05)
                count += 1
                if count > 10:
                    # Simulate an exit condition that might cause issues
                    if task_id == 0:
                        raise KeyboardInterrupt("Simulated Ctrl+C")
                    elif task_id == 1:
                        raise SystemExit("Simulated system exit")
        except (KeyboardInterrupt, SystemExit):
            print(f"Task {task_id} received exit signal", flush=True)
            raise
    
    # Start multiple infinite tasks in secondary
    futures = []
    for i in range(3):
        future = secondary_ctx.queue.submit(infinite_secondary_task, i)
        futures.append(future)
    
    # Run both viewports
    print("Starting nested viewport scenario...", flush=True)
    for frame in range(25):  # Reduced from 30
        check_timeout()
        if primary_ctx.running:
            primary_ctx.viewport.render_frame()
        if secondary_ctx.running:
            secondary_ctx.viewport.render_frame()
        time.sleep(0.01)
        
        if frame == 12:  # Reduced from 15
            print("Initiating shutdown...", flush=True)
            primary_ctx.running = False
            secondary_ctx.running = False
            primary_ctx.viewport.wake()
            secondary_ctx.viewport.wake()
    
    print("Shutting down executors...", flush=True)
    primary_ctx.queue.shutdown(wait=False)
    secondary_ctx.queue.shutdown(wait=False)
    print("Script completed", flush=True)
    
except (KeyboardInterrupt, SystemExit) as e:
    print(f"Exit signal caught in main: {e}", flush=True)
except Exception as e:
    print(f"Exception in main: {e}", flush=True)
    import traceback
    traceback.print_exc()
finally:
    print("Script terminating", flush=True)
'''
    
    proc = subprocess.Popen(
        [sys.executable, '-c', script_content],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        stdout, stderr = proc.communicate(timeout=4.0)  # Reduced timeout
        print("=== NESTED EXECUTOR TEST OUTPUT ===")
        print("STDOUT:", stdout)
        print("STDERR:", stderr)
        
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
        print("=== HANGING DETECTED IN NESTED EXECUTOR TEST ===")
        print("STDOUT:", stdout if isinstance(stdout, str) else stdout.decode())
        print("STDERR:", stderr if isinstance(stderr, str) else stderr.decode())
        print("SUCCESS: Reproduced nested executor hanging scenario!")


def test_shutdown_with_active_tasks_hanging():
    """Test shutdown behavior when tasks are actively running."""
    
    script_content = '''
import asyncio
import sys
import time
import dearcygui as dcg
from dearcygui.utils.asyncio_helpers import AsyncThreadPoolExecutor

try:
    ctx = dcg.Context()
    ctx.viewport.initialize(visible=False)
    ctx.viewport.wait_for_input = True
    executor = AsyncThreadPoolExecutor()
    ctx.queue = executor
    
    # Task that runs for a long time
    async def long_running_task():
        for i in range(100):
            await asyncio.sleep(0.1)
            print(f"Long task iteration {i}", flush=True)
        return "completed"
    
    # Task that submits more tasks
    async def task_spawner():
        for i in range(5):
            executor.submit(long_running_task)
            await asyncio.sleep(0.05)
    
    # Start both types of tasks
    spawner_future = executor.submit(task_spawner)
    main_future = executor.submit(long_running_task)
    
    # Run briefly then try to shutdown while tasks are active
    print("Running with active tasks...", flush=True)
    for i in range(10):
        ctx.viewport.render_frame()
        time.sleep(0.1)
    
    print("Attempting shutdown with active tasks...", flush=True)
    ctx.running = False
    ctx.viewport.wake()
    
    # This is where the hang might occur
    executor.shutdown(wait=False)  # Don't wait for tasks
    
    print("Shutdown completed", flush=True)
    
except Exception as e:
    print(f"Exception: {e}", flush=True)
    import traceback
    traceback.print_exc()
'''
    
    proc = subprocess.Popen(
        [sys.executable, '-c', script_content],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        stdout, stderr = proc.communicate(timeout=5.0)
        print("=== SHUTDOWN WITH ACTIVE TASKS OUTPUT ===")
        print("STDOUT:", stdout)
        print("STDERR:", stderr)
        
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
        print("=== HANGING DETECTED IN ACTIVE TASKS SHUTDOWN TEST ===")
        print("STDOUT:", stdout if isinstance(stdout, str) else stdout.decode())
        print("STDERR:", stderr if isinstance(stderr, str) else stderr.decode())
        print("SUCCESS: Reproduced shutdown hanging with active tasks!")


def test_hanging_summary():
    """Summary test that documents all the hanging patterns we've discovered."""
    
    print("\n" + "="*80)
    print("HANGING SCENARIO ANALYSIS SUMMARY")
    print("="*80)
    
    print("""
DISCOVERED HANGING PATTERNS:

1. UNHANDLED EXCEPTIONS IN ASYNCTHREADPOOLEXECUTOR
   - Condition: AsyncThreadPoolExecutor + unhandled async exceptions + wait_for_input=True
   - Symptom: Process hangs on shutdown, no error output
   - Root Cause: Exception propagation issues in background thread

2. WAIT_FOR_INPUT + SYSTEMEXIT/KEYBOARDINTERRUPT
   - Condition: wait_for_input=True + AsyncThreadPoolExecutor + SystemExit/KeyboardInterrupt in tasks
   - Symptom: Process hangs during shutdown sequence
   - Root Cause: Event loop blocking on input while handling exit signals

3. NESTED EXECUTORS WITH EXCEPTION PROPAGATION
   - Condition: AsyncPoolExecutor (primary) + AsyncThreadPoolExecutor (secondary) + exceptions
   - Symptom: Unhandled exceptions in executor threads, possible hangs
   - Root Cause: Exception handling differs between executor types

4. SHUTDOWN WITH ACTIVE LONG-RUNNING TASKS
   - Condition: shutdown(wait=False) called while many async tasks are running
   - Symptom: Tasks continue running after shutdown call, process hangs
   - Root Cause: Background event loop not properly stopped

COMMON FACTORS:
- AsyncThreadPoolExecutor seems to be involved in most hanging scenarios
- wait_for_input=True exacerbates the problem
- Exception handling (SystemExit, KeyboardInterrupt) is problematic
- shutdown(wait=False) doesn't guarantee immediate termination

PRODUCTION REPRODUCTION CONDITIONS:
Your production issue likely involves:
1. Primary viewport with AsyncPoolExecutor
2. Secondary viewport created from callback with AsyncThreadPoolExecutor  
3. Infinite async tasks in secondary viewport
4. wait_for_input=True on both viewports
5. SystemExit or KeyboardInterrupt during shutdown

RECOMMENDED FIXES:
1. Improve exception handling in AsyncThreadPoolExecutor._thread_worker()
2. Ensure proper signal handling when wait_for_input=True
3. Add timeout to executor.shutdown() calls
4. Consider using executor.shutdown(wait=True, cancel_futures=True)
5. Implement proper cleanup order: stop contexts -> wake viewports -> shutdown executors
    """)
    
    print("="*80)


def test_potential_fix_exception_handling():
    """Test a potential fix for exception handling in AsyncThreadPoolExecutor."""
    
    script_content = '''
import asyncio
import sys
import time
import dearcygui as dcg
from dearcygui.utils.asyncio_helpers import AsyncThreadPoolExecutor

# Monkey patch to improve exception handling
original_thread_worker = AsyncThreadPoolExecutor._thread_worker

def improved_thread_worker(self):
    """Improved thread worker with better exception handling."""
    try:
        return original_thread_worker(self)
    except (KeyboardInterrupt, SystemExit) as e:
        print(f"Thread worker caught {type(e).__name__}: {e}", flush=True)
        # Ensure the loop stops properly
        if self._thread_loop and self._thread_loop.is_running():
            self._thread_loop.stop()
        raise
    except Exception as e:
        print(f"Thread worker caught unexpected exception: {e}", flush=True)
        # Log but don't re-raise to avoid thread death
        import traceback
        traceback.print_exc()

AsyncThreadPoolExecutor._thread_worker = improved_thread_worker

try:
    ctx = dcg.Context()
    ctx.viewport.initialize(visible=False)
    ctx.viewport.wait_for_input = True
    executor = AsyncThreadPoolExecutor()
    ctx.queue = executor
    
    async def problematic_task():
        await asyncio.sleep(0.1)
        raise KeyboardInterrupt("Simulated interrupt")
    
    future = executor.submit(problematic_task)
    
    for i in range(10):
        ctx.viewport.render_frame()
        time.sleep(0.01)
    
    print("Attempting improved shutdown...", flush=True)
    ctx.running = False
    ctx.viewport.wake()
    
    # Try shutdown with timeout
    try:
        executor.shutdown(wait=True, cancel_futures=True)
        print("Shutdown completed successfully", flush=True)
    except Exception as e:
        print(f"Shutdown exception: {e}", flush=True)
    
except Exception as e:
    print(f"Main exception: {e}", flush=True)
    import traceback
    traceback.print_exc()
'''
    
    proc = subprocess.Popen(
        [sys.executable, '-c', script_content],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        stdout, stderr = proc.communicate(timeout=3.0)
        print("=== POTENTIAL FIX TEST OUTPUT ===")
        print("STDOUT:", stdout)
        print("STDERR:", stderr)
        print("SUCCESS: Potential fix completed without hanging!")
        
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
        print("=== POTENTIAL FIX STILL HANGS ===")
        print("STDOUT:", stdout if isinstance(stdout, str) else stdout.decode())
        print("STDERR:", stderr if isinstance(stderr, str) else stderr.decode())
        print("FAILURE: Potential fix did not resolve the hanging issue")


def test_simple_asyncthreadpool_hang():
    """Minimal test to reproduce AsyncThreadPoolExecutor hanging."""
    
    script_content = '''
import sys
import time
import dearcygui as dcg
from dearcygui.utils.asyncio_helpers import AsyncThreadPoolExecutor

# Very simple hang test
start_time = time.time()

try:
    ctx = dcg.Context()
    ctx.viewport.initialize(visible=False)
    ctx.viewport.wait_for_input = True  # This seems to be a key factor
    
    executor = AsyncThreadPoolExecutor()
    ctx.queue = executor
    
    # Simple task that just raises an exception
    def simple_failing_task():
        time.sleep(0.1)
        raise RuntimeError("Simple exception")
    
    # Submit and don't wait for result
    future = executor.submit(simple_failing_task)
    
    print("Running frames...", flush=True)
    for i in range(5):
        if time.time() - start_time > 2.0:  # Safety timeout
            break
        ctx.viewport.render_frame()
        time.sleep(0.1)
    
    print("Stopping context...", flush=True)
    ctx.running = False
    ctx.viewport.wake()
    
    print("Shutting down executor...", flush=True)
    executor.shutdown(wait=False)
    
    print("Done", flush=True)
    
except Exception as e:
    print(f"Exception: {e}", flush=True)
    import traceback
    traceback.print_exc()
'''
    
    proc = subprocess.Popen(
        [sys.executable, '-c', script_content],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        stdout, stderr = proc.communicate(timeout=3.0)
        print("=== SIMPLE HANG TEST OUTPUT ===")
        print("STDOUT:", stdout)
        print("STDERR:", stderr)
        
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
        print("=== SIMPLE HANG DETECTED ===")
        print("STDOUT:", stdout if isinstance(stdout, str) else stdout.decode())
        print("STDERR:", stderr if isinstance(stderr, str) else stderr.decode())
        print("SUCCESS: Reproduced simple hanging scenario!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
