import threading
import time
from typing import List, Tuple, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

class ConcurrentJobHandler:
    """Module 4: Concurrent Job Submission Handling
    # Author: [glen Moses]
    # Description: Handles simultaneous job submissions with thread safety
    This class provides thread-safe methods for simultaneous job submissions.
    """

    def __init__(self, max_threads: int = 5):
        """Initialize the concurrent job handler.

        Args:
            max_threads: Maximum number of concurrent threads for job submission
        """
        self._max_threads = max_threads
        self._submission_lock = threading.Lock()

    def handle_simultaneous_submissions(self, print_queue, jobs: List[Tuple[str, int]]) -> Dict[str, Any]:
        """Handle simultaneous job submissions with thread safety.

        Args:
            print_queue: The CircularPrintQueue instance to submit jobs to
            jobs: List of tuples containing (user_id, priority) for each job

        Returns:
            Dictionary with submission results and statistics
        """
        if not jobs:
            return {
                'success_count': 0,
                'failed_count': 0,
                'execution_time': 0,
                'message': 'No jobs to submit'
            }

        start_time = time.time()
        results = []

        # Use ThreadPoolExecutor for controlled concurrent execution
        with ThreadPoolExecutor(max_workers=min(self._max_threads, len(jobs))) as executor:
            # Submit all jobs concurrently
            future_to_job = {
                executor.submit(self._submit_single_job, print_queue, user_id, priority, idx)
                for idx, (user_id, priority) in enumerate(jobs)
            }

            # Collect results as they complete
            for future in as_completed(future_to_job):
                user_id, priority, original_index = future_to_job[future]
                try:
                    # Simulate some processing time to make concurrency more apparent
                    time.sleep(0.01)  # 10ms delay

                    result = future.result(timeout=5.0)  # 5 second timeout per job
                    results.append({
                        'user_id': user_id,
                        'priority': priority,
                        'original_index': original_index,
                        'success': result['success'],
                        'job_id': result.get('job_id', ''),
                        'message': result.get('message', ''),
                        'thread_id': result.get('thread_id'),
                    })
                except Exception as e:
                    results.append({
                        'user_id': user_id,
                        'priority': priority,
                        'original_index': original_index,
                        'success': False,
                        'job_id': None,
                        'message': f'Exception during submission: {str(e)}',
                        'thread_id': threading.current_thread().ident,
                    })

        # Sort results by original submission order
        results.sort(key=lambda x: x['original_index'])

        # Calculate statistics
        success_count = sum(1 for x in results if x['success'])
        failed_count = len(results) - success_count
        execution_time = time.time() - start_time

        return {
            'success_count': success_count,
            'failed_count': failed_count,
            'execution_time': round(execution_time, 4),
            'message': f'Processed {len(jobs)} simultaneous submissions: {success_count} succeeded, {failed_count} failed',
        }

    def _submit_single_job(self, print_queue, user_id: str, priority: int, submission_index: int) -> Dict[str, Any]:
        """Thread-safe single job submission with proper synchronization.

        Args:
            print_queue: The CircularPrintQueue instance
            user_id: User identifier
            priority: Job priority
            submission_index: Original index in the submission batch

        Returns:
            Dictionary with submission result
        """
        thread_id = threading.current_thread().ident

        try:
            # Simulate some processing time to make concurrency more apparent
            time.sleep(0.01)  # 10ms delay

            # Thread-safe job submission
            with self._submission_lock:
                # Double-check queue capacity before submission
                if print_queue.is_full():
                    return {
                        'success': False,
                        'message': f'Queue full when submitting job for {user_id}',
                        'thread_id': thread_id
                    }

                # Attempt to enqueue the job
                success = print_queue.enqueue(user_id, priority)

                if success:
                    # Get the job ID of the newly added job
                    job_id = print_queue.job_counter
                    return {
                        'success': True,
                        'job_id': job_id,
                        'message': f'Successfully enqueued job for {user_id}',
                        'thread_id': thread_id
                    }
                else:
                    return {
                        'success': False,
                        'message': f'Failed to enqueue job for {user_id} - queue may be full',
                        'thread_id': thread_id
                    }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error submitting job for {user_id}: {str(e)}',
                'thread_id': thread_id
            }

    def parse_simultaneous_command(self, job_data: str) -> List[Tuple[str, int]]:
        """Parse simultaneous job submission command string.

        Expected format: "user1:priority1,user2:priority2,user3:priority3"

        Args:
            job_data: Comma-separated string of user:priority pairs

        Returns:
            List of (user_id, priority) tuples

        Raises:
            ValueError: If the format is invalid
        """
        if not job_data.strip():
            return []

        jobs = []
        job_pairs = job_data.split(',')

        for pair in job_pairs:
            if ':' not in pair:
                raise ValueError(f'Invalid job format \'{pair}\'. Expected \'user:priority\'')
            try:
                user_id, priority_str = pair.strip().split(':', 1)
                priority = int(priority_str.strip())
                jobs.append((user_id.strip(), priority))
            except ValueError:
                raise ValueError(f'Invalid priority \'{priority_str}\' for user \'{user_id}\'')

        return jobs

    def format_submission_results(self, result: Dict[Any, Any], job_count: int) -> str:
        """Format the submission results for display.

        Args:
            result: Result dictionary from handle_simultaneous_submissions
            job_count: Number of jobs originally submitted

        Returns:
            Formatted result string
        """
        output_lines = [
            f"SIMULTANEOUS SUBMISSION RESULTS ==",
            f"Jobs submitted: {job_count}",
            f"Successful: {result['success_count']}",
            f"Failed: {result['failed_count']}",
            f"Execution time: {result['execution_time']}s",
            "Individual Results:"
        ]

        for x in result['results']:
            status = "✓" if x['success'] else "✗"
            job_info = f"Job #{x['job_id']}" if x['job_id'] else "No Job ID"
            output_lines.append(
                f"  {status} {x['user_id']} (pri: {x['priority']}) -> {job_info} | {x['message']}"
            )

        return "\n".join(output_lines)
