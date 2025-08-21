from typing import Any, Dict, Optional, Union

from pydantic import BaseModel


class JobStatus(BaseModel):
    """Status information for a CVAT job.

    Jobs are subdivisions of tasks that can be assigned to different annotators.
    Each job has a stage (e.g., "annotation") and state (e.g., "completed").

    Attributes:
        task_id: ID of the task this job belongs to
        job_id: Unique identifier for the job
        task_name: Name of the parent task
        stage: Current stage of the job (e.g., "annotation", "validation")
        state: Current state of the job (e.g., "completed", "in_progress")
        assignee: Username or details of the person assigned to the job

    Example:
        ```python
        # Create from job status data
        status = JobStatus(
            task_id="906591",
            job_id=520016,
            task_name="Batch 1",
            stage="annotation",
            state="completed",
            assignee="john.doe"
        )

        # Create from CVAT SDK job object
        status = JobStatus.from_job(job, task_name="Batch 1")
        print(status.assignee_email)  # Get assignee's email
        ```
    """

    task_id: str
    job_id: int
    task_name: str
    stage: str
    state: str
    assignee: Optional[Union[str, Dict[str, Any]]] = None

    @classmethod
    def from_job(cls, job, task_name: str):
        """Create a JobStatus from a CVAT SDK job object."""
        assignee = job.assignee
        if hasattr(assignee, '__dict__'):
            assignee = {k: v for k, v in assignee.__dict__.items() if not k.startswith('_')}
        elif hasattr(assignee, 'to_dict'):
            assignee = assignee.to_dict()

        return cls(
            task_id=str(job.task_id),
            job_id=job.id,
            task_name=task_name,
            stage=job.stage,
            state=job.state,
            assignee=assignee,
        )

    @property
    def assignee_email(self) -> Optional[str]:
        """Get the assignee's email if available."""
        if isinstance(self.assignee, dict):
            return self.assignee.get('username')
        return self.assignee 