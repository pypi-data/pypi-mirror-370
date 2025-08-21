from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Union
from xml.etree import ElementTree

from pydantic import BaseModel

from .types import (
    Attribute,
    Box,
    Ellipse,
    ImageAnnotation,
    JobStatus,
    Label,
    Mask,
    Polygon,
    Polyline,
    Project,
    Tag,
    Task,
)


class Annotations(BaseModel):
    """CVAT annotations for managing project, task, and image data.

    This class provides functionality to:
    - Load and save CVAT XML annotation files
    - Track job status information
    - Query task completion status
    - Access image annotations

    Examples:
        Load annotations from XML file:
        ```python
        annotations = Annotations.from_path("annotations.xml")
        ```

        Load annotations with job status:
        ```python
        annotations = Annotations.from_path(
            "annotations.xml",
            "job_status.json"
        )
        ```

        Get completed tasks and their images:
        ```python
        completed_tasks = annotations.get_completed_tasks()
        completed_images = annotations.get_images_from_completed_tasks()
        ```
    """

    version: str
    project: Project
    tasks: List[Task]
    images: List[ImageAnnotation]
    job_status: List[JobStatus] = []

    @classmethod
    def from_path(
        cls,
        xml_annotation_path: Union[str, Path],
        job_status_path: Optional[Union[str, Path]] = None,
    ) -> Annotations:
        """Load annotations from XML file and optionally include job status information.

        Args:
            xml_annotation_path: Path to the CVAT XML annotations file
            job_status_path: Optional path to the job status JSON file

        Returns:
            Annotations object containing the loaded data

        Example:
            ```python
            # Load just annotations
            annotations = Annotations.from_path("annotations.xml")

            # Load annotations with job status
            annotations = Annotations.from_path(
                "annotations.xml",
                "job_status.json"
            )
            ```
        """
        tree = ElementTree.parse(str(xml_annotation_path))
        root = tree.getroot()

        # Parse project details
        project = root.find("meta/project")
        labels = []
        for label in project.findall("labels/label"):
            attributes = [
                Attribute(**attr.attrib)
                for attr in label.findall("attributes/attribute")
                if len(attr.keys()) >= 1
            ]
            label_data = Label(
                name=label.find("name").text,
                color=label.find("color").text,
                type=label.find("type").text,
                attributes=attributes,
            )
            labels.append(label_data)

        project_data = Project(
            id=project.find("id").text,
            name=project.find("name").text,
            created=project.find("created").text,
            updated=project.find("updated").text,
            labels=labels,
        )

        # Parse tasks and store task_id to job_id mapping
        tasks = []
        task_job_mapping = {}
        task_locations = ["meta/tasks/task", "meta/project/tasks/task"]
        for location in task_locations:
            for task in root.findall(location):
                task_id = task.find("id").text
                name = task.find("name").text
                url_tag = task.find("segments/segment/url")
                if url_tag is not None:
                    task_instance = Task(task_id=task_id, name=name, url=url_tag.text)
                    tasks.append(task_instance)
                    # Extract job_id from URL if available
                    if url_tag.text:
                        try:
                            job_id = url_tag.text.split("/")[-1]
                            task_job_mapping[task_id] = job_id
                        except (IndexError, AttributeError):
                            pass

        # Parse image annotations
        images = []
        for image in root.findall("image"):
            boxes = []
            for box in image.findall("box"):
                box_attributes = [
                    Attribute(name=attr.get("name"), value=attr.text)
                    for attr in box.findall("attribute")
                ]
                boxes.append(Box(**box.attrib, attributes=box_attributes))

            polygons = []
            for polygon in image.findall("polygon"):
                polygon_attributes = [
                    Attribute(name=attr.get("name"), value=attr.text)
                    for attr in polygon.findall("attribute")
                ]
                polygons.append(
                    Polygon(**polygon.attrib, attributes=polygon_attributes)
                )

            masks = []
            for mask in image.findall("mask"):
                mask_attributes = [
                    Attribute(name=attr.get("name"), value=attr.text)
                    for attr in mask.findall("attribute")
                ]
                masks.append(Mask(**mask.attrib, attributes=mask_attributes))

            polylines = []
            for polyline in image.findall("polyline"):
                polyline_attributes = [
                    Attribute(name=attr.get("name"), value=attr.text)
                    for attr in polyline.findall("attribute")
                ]
                polylines.append(
                    Polyline(**polyline.attrib, attributes=polyline_attributes)
                )

            ellipses = []
            for ellipse in image.findall("ellipse"):
                ellipse_attributes = [
                    Attribute(name=attr.get("name"), value=attr.text)
                    for attr in ellipse.findall("attribute")
                ]
                ellipses.append(
                    Ellipse(**ellipse.attrib, attributes=ellipse_attributes)
                )

            # Parse tags
            tags = []
            for tag in image.findall("tag"):
                tag_attributes = [
                    Attribute(name=attr.get("name"), value=attr.text)
                    for attr in tag.findall("attribute")
                ]
                tags.append(
                    Tag(
                        label=tag.get("label"),
                        source=tag.get("source", "manual"),
                        attributes=tag_attributes,
                    )
                )

            # Get job_id from task_job_mapping if available
            task_id = image.get("task_id")
            job_id = task_job_mapping.get(task_id) if task_id else None

            images.append(
                ImageAnnotation(
                    id=image.get("id"),
                    name=image.get("name"),
                    subset=image.get("subset"),
                    task_id=task_id,
                    job_id=job_id,
                    width=int(image.get("width")),
                    height=int(image.get("height")),
                    boxes=boxes,
                    polygons=polygons,
                    masks=masks,
                    polylines=polylines,
                    ellipses=ellipses,
                    tags=tags,
                )
            )

        # Load job status if provided
        job_status = []
        if job_status_path:
            with open(job_status_path) as f:
                job_status_data = json.load(f)
                job_status = [JobStatus(**status) for status in job_status_data]

        return cls(
            version=root.find("version").text,
            project=project_data,
            tasks=tasks,
            images=images,
            job_status=job_status,
        )

    def save_xml_(self, path: Union[str, Path]) -> Annotations:
        """
        Save annotations to XML file in CVAT format.

        Args:
            path: Path where to save the XML file
        """
        root = ElementTree.Element("annotations")

        # Add version
        version = ElementTree.SubElement(root, "version")
        version.text = self.version

        # Add meta section with project info
        meta = ElementTree.SubElement(root, "meta")
        project = ElementTree.SubElement(meta, "project")

        # Project details
        project_id = ElementTree.SubElement(project, "id")
        project_id.text = self.project.id

        project_name = ElementTree.SubElement(project, "name")
        project_name.text = self.project.name

        created = ElementTree.SubElement(project, "created")
        created.text = self.project.created

        updated = ElementTree.SubElement(project, "updated")
        updated.text = self.project.updated

        # Add labels
        labels_elem = ElementTree.SubElement(project, "labels")
        for label in self.project.labels:
            label_elem = ElementTree.SubElement(labels_elem, "label")

            name = ElementTree.SubElement(label_elem, "name")
            name.text = label.name

            color = ElementTree.SubElement(label_elem, "color")
            color.text = label.color

            type_elem = ElementTree.SubElement(label_elem, "type")
            type_elem.text = label.type

            if label.attributes:
                attrs_elem = ElementTree.SubElement(label_elem, "attributes")
                for attr in label.attributes:
                    attr_elem = ElementTree.SubElement(attrs_elem, "attribute")
                    for key, value in attr.model_dump().items():
                        if value is not None:
                            attr_elem.set(key, str(value))

        # Add tasks
        if self.tasks:
            tasks_elem = ElementTree.SubElement(meta, "tasks")
            for task in self.tasks:
                task_elem = ElementTree.SubElement(tasks_elem, "task")
                task_id = ElementTree.SubElement(task_elem, "id")
                task_id.text = task.task_id
                task_name = ElementTree.SubElement(task_elem, "name")
                task_name.text = task.name

                segments = ElementTree.SubElement(task_elem, "segments")
                segment = ElementTree.SubElement(segments, "segment")
                if task.url:
                    url = ElementTree.SubElement(segment, "url")
                    url.text = task.url

        # Add image annotations
        for image in self.images:
            image_elem = ElementTree.Element("image")
            image_elem.set("id", image.id)
            image_elem.set("name", image.name)
            if image.subset:
                image_elem.set("subset", image.subset)
            if image.task_id:
                image_elem.set("task_id", image.task_id)
            if image.job_id:
                image_elem.set("job_id", image.job_id)
            image_elem.set("width", str(image.width))
            image_elem.set("height", str(image.height))

            # Add boxes
            for box in image.boxes:
                box_elem = ElementTree.SubElement(image_elem, "box")
                for key, value in box.model_dump().items():
                    if key != "attributes" and value is not None:
                        box_elem.set(key, str(value))

                if box.attributes:
                    for attr in box.attributes:
                        attr_elem = ElementTree.SubElement(box_elem, "attribute")
                        attr_elem.set("name", attr.name)
                        attr_elem.text = attr.value

            # Add polygons
            for polygon in image.polygons:
                poly_elem = ElementTree.SubElement(image_elem, "polygon")
                for key, value in polygon.model_dump().items():
                    if key != "attributes" and value is not None:
                        poly_elem.set(key, str(value))

                if polygon.attributes:
                    for attr in polygon.attributes:
                        attr_elem = ElementTree.SubElement(poly_elem, "attribute")
                        attr_elem.set("name", attr.name)
                        attr_elem.text = attr.value

            # Add masks
            for mask in image.masks:
                mask_elem = ElementTree.SubElement(image_elem, "mask")
                for key, value in mask.model_dump().items():
                    if key != "attributes" and value is not None:
                        mask_elem.set(key, str(value))

                if mask.attributes:
                    for attr in mask.attributes:
                        attr_elem = ElementTree.SubElement(mask_elem, "attribute")
                        attr_elem.set("name", attr.name)
                        attr_elem.text = attr.value

            # Add polylines
            for polyline in image.polylines:
                line_elem = ElementTree.SubElement(image_elem, "polyline")
                for key, value in polyline.model_dump().items():
                    if key != "attributes" and value is not None:
                        line_elem.set(key, str(value))

                if polyline.attributes:
                    for attr in polyline.attributes:
                        attr_elem = ElementTree.SubElement(line_elem, "attribute")
                        attr_elem.set("name", attr.name)
                        attr_elem.text = attr.value

            # Add ellipses
            for ellipse in image.ellipses:
                ellipse_elem = ElementTree.SubElement(image_elem, "ellipse")
                for key, value in ellipse.model_dump().items():
                    if key != "attributes" and value is not None:
                        ellipse_elem.set(key, str(value))

                if ellipse.attributes:
                    for attr in ellipse.attributes:
                        attr_elem = ElementTree.SubElement(ellipse_elem, "attribute")
                        attr_elem.set("name", attr.name)
                        attr_elem.text = attr.value

            # Add tags
            for tag in image.tags:
                tag_elem = ElementTree.SubElement(image_elem, "tag")
                tag_elem.set("label", tag.label)
                tag_elem.set("source", tag.source)

                if tag.attributes:
                    for attr in tag.attributes:
                        attr_elem = ElementTree.SubElement(tag_elem, "attribute")
                        attr_elem.set("name", attr.name)
                        attr_elem.text = attr.value

            root.append(image_elem)

        # Create XML tree and save to file
        tree = ElementTree.ElementTree(root)
        tree.write(str(path), encoding="utf-8", xml_declaration=True)

        return self

    def get_task_status(self, task_id: str) -> Dict[str, str]:
        """Get the status of all jobs for a given task.

        Args:
            task_id: ID of the task to get status for

        Returns:
            Dictionary mapping job IDs to their states

        Example:
            ```python
            task_status = annotations.get_task_status("1234")
            # Returns: {"5678": "completed", "5679": "in_progress"}
            ```
        """
        # Find the job ID from the task URL
        job_id = None
        for task in self.tasks:
            if task.task_id == task_id and task.url:
                job_id = task.url.split("/")[-1]
                break

        if job_id is None:
            return {}

        # Map the job ID to its status
        return {
            job_id: status.state
            for status in self.job_status
            if status.task_id == task_id
        }

    def get_completed_tasks(self) -> List[Task]:
        """Get all tasks that have all jobs completed.

        A task is considered completed when all of its jobs are in the "completed" state.

        Returns:
            List of Task objects that are fully completed

        Example:
            ```python
            completed_tasks = annotations.get_completed_tasks()
            for task in completed_tasks:
                print(f"Task {task.task_id}: {task.name}")
            ```
        """
        completed_task_ids = self.get_completed_task_ids()
        return [task for task in self.tasks if task.task_id in completed_task_ids]

    def get_completed_task_ids(self) -> List[str]:
        """Get IDs of all tasks that have all jobs completed.

        A task is considered completed when all of its jobs are in the "completed" state.

        Returns:
            List of task IDs that are fully completed

        Example:
            ```python
            completed_ids = annotations.get_completed_task_ids()
            # Returns: ["1234", "5678"]
            ```
        """
        task_statuses = {}
        for status in self.job_status:
            if status.task_id not in task_statuses:
                task_statuses[status.task_id] = []
            task_statuses[status.task_id].append(status.state)

        return [
            task_id
            for task_id, states in task_statuses.items()
            if len(states) > 0 and all(state == "completed" for state in states)
        ]

    def get_images_from_completed_tasks(self) -> List[ImageAnnotation]:
        """Get all images from completed tasks.

        Returns:
            List of ImageAnnotation objects from completed tasks

        Example:
            ```python
            completed_images = annotations.get_images_from_completed_tasks()
            for image in completed_images:
                print(f"Image {image.name} from task {image.task_id}")
            ```
        """
        completed_task_ids = self.get_completed_task_ids()
        return [image for image in self.images if image.task_id in completed_task_ids]

    def create_cvat_link(self, image_name: str) -> str:
        """Create a CVAT link for the given image name.

        Args:
            image_name: Name of the image

        Returns:
            A CVAT link in the format: https://app.cvat.ai/tasks/{task_id}/jobs/{job_id}?frame={frame_index}

        Raises:
            ValueError: If the image or its associated job is not found

        Example:
            ```python
            link = annotations.create_cvat_link("image1.jpg")
            # Returns: "https://app.cvat.ai/tasks/453747/jobs/520016?frame=0"
            ```
        """
        images = list(sorted(self.images, key=lambda image: image.name))

        # lookup task id for the given image name
        task_id = None
        job_id = None
        for image in images:
            if Path(image.name).name == image_name:
                job_id = image.job_id
                task_id = image.task_id
                break

        frame_index = 0
        for image in images:
            if image.task_id == task_id:
                if Path(image.name).name == image_name:
                    break
                frame_index += 1

        if task_id is None:
            raise ValueError(f"Image {image_name} not found")

        if job_id is None:
            raise ValueError(f"No job found for task {task_id}")

        return f"https://app.cvat.ai/tasks/{task_id}/jobs/{job_id}?frame={frame_index}"
