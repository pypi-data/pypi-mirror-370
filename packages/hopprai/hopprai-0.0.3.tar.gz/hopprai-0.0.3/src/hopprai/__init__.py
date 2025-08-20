import os
from dataclasses import dataclass
import requests
import time
from typing import List, Optional

__version__ = "0.0.3"


@dataclass
class Image:
  """
  Represents an image associated with a study.

  Attributes:
      id (str): Unique identifier for the image.
      reference (str): Reference string for the image.
      deidentified (bool): Indicates if the image has been deidentified.
      uploaded (bool): Indicates if the image has been uploaded.
  """

  id: str
  reference: str
  deidentified: bool
  uploaded: bool


@dataclass
class Study:
  """
  Represents a study containing multiple images.

  Attributes:
      id (str): Unique identifier for the study.
      reference (str): Reference string for the study.
      images (List[Image]): List of images associated with the study.
  """

  id: str
  reference: str
  images: List[Image]


@dataclass
class ModelResponse:
  """
  Represents the response from a model inference.

  Attributes:
      success (bool): Indicates if the inference was successful.
      response (str): The response message from the model.
  """

  success: bool
  response: str


@dataclass
class DatasetStatus:
  """
  Represents the status of a dataset

  Attributes:
      total_images (int): The total number of images in the dataset
      invalid_count (int): The number of invalid images in the dataset
      deided_count (int): The number of deidentified images in the dataset
  """

  total_images: int
  invalid_count: int
  deided_count: int


class HOPPR:
  """
  SDK for interacting with the HOPPR API.

  Provides methods for managing studies, adding images, interacting with models, managing datasets and training jobs.
  """

  def __init__(self, api_key: str, base_url="https://api.hoppr.ai"):
    """
    Initializes the HopprSdk instance.

    Args:
        api_key (str): API key for authenticating with the Hoppr API.
        base_url (str): Base URL for the Hoppr API (default is "https://api.hoppr.ai").
    """
    self.default_headers = {"x-api-key": api_key, "Accept": "application/json", "Content-Type": "application/json"}
    self.base_url = base_url

  def get_study(self, study_id: str) -> Optional[Study]:
    """
    Retrieves a study by its id.

    Args:
        study_id (str): The unique identifier of the study to retrieve.

    Returns:
        Optional[Study]: The study if found, otherwise None.

    Raises:
        RuntimeError: If an unsuccessful response is received from the server.
    """
    response = requests.get(url=f"{self.base_url}/studies/{study_id}", headers=self.default_headers)
    if response.status_code == 404:
      return None
    elif response.status_code != 200:
      raise RuntimeError(
        f"Received unsuccessful response while retrieving study.\nStatus code: {response.status_code}: {response.text}"
      )
    return self.__study_from_json(response.json())

  def search_studies(self, reference: str) -> list[Study]:
    """
    Retrieves studies by a reference.

    Args:
        reference (str): The reference of the study or studies to retrieve.

    Returns:
        list[Study]: A list of studies, empty if not found.

    Raises:
        RuntimeError: If an unsuccessful response is received from the server.
    """
    response = requests.get(
      url=f"{self.base_url}/search", headers=self.default_headers, params={"reference": reference}
    )
    if response.status_code != 200:
      raise RuntimeError(
        (
          f"Received unsuccessful response while retrieving studies with reference.\n"
          f"Status code: {response.status_code}: {response.text}"
        )
      )
    return self.__studies_from_json(response.json())

  def create_study(self, reference: str) -> Study:
    """
    Creates a new study.

    Args:
        reference (str): Reference string for the new study.

    Returns:
        Study: The created study.

    Raises:
        RuntimeError: If an unsuccessful response is received from the server.
    """
    response = requests.post(
      url=f"{self.base_url}/studies",
      headers=self.default_headers,
      json={"reference": reference},
    )
    if response.status_code != 201:
      raise RuntimeError(
        f"Received unsuccessful response while creating study.\nStatus code: {response.status_code}, {response.text}"
      )
    return self.__study_from_json(response.json())

  def delete_study(self, study_id: str) -> bool:
    """
    Deletes a study by its ID.

    Args:
        study_id (str): The unique identifier of the study to delete.

    Returns:
        bool: True if the study was successfully deleted, otherwise False.
    """
    response = requests.delete(url=f"{self.base_url}/studies/{study_id}", headers=self.default_headers)
    return response.status_code == 204

  def add_study_image(self, study_id: str, reference: str, image: bytes) -> Image:
    """
    Adds an image to a study.

    Args:
        study_id (str): The unique identifier of the study.
        reference (str): Reference string for the image.
        image (bytes): The image data to be uploaded.

    Returns:
        Image: The added image.

    Raises:
        RuntimeError: If an unsuccessful response is received during the process.
    """
    presigned_response = requests.post(
      url=f"{self.base_url}/studies/{study_id}/images",
      headers=self.default_headers,
      json={"reference": reference},
    )
    if presigned_response.status_code != 201:
      raise RuntimeError(
        f"""
        Received unsuccessful response while adding an image to study.
        Status code: {presigned_response.status_code}, {presigned_response.status_code}
        """
      )
    presigned = presigned_response.json()
    presigned_url = presigned["url"]
    fields = presigned["fields"]
    files = {"file": image}
    upload_response = requests.post(url=presigned_url, data=fields, files=files)
    if upload_response.status_code != 204:
      raise RuntimeError(f"Unable to upload image.\nStatus code: {upload_response.status_code}, {upload_response.text}")
    return Image(id=presigned["id"], reference=reference, deidentified=False, uploaded=True)

  def delete_study_image(self, study_id: str, image_id: str) -> bool:
    """
    Deletes an image from a study.

    Args:
        study_id (str): The unique identifier of the study.
        image_id (str): The unique identifier of the image to delete.

    Returns:
        bool: True if the image was successfully deleted, otherwise False.
    """
    response = requests.delete(
      url=f"{self.base_url}/studies/{study_id}/images/{image_id}",
      headers=self.default_headers,
    )
    return response.status_code == 204

  def prompt_model(
    self,
    study_id: str,
    model: str,
    prompt: str,
    timeout: int = 180,
    response_format: str = "text",
  ) -> Optional[ModelResponse]:
    """
    Prompts a model for inference and waits for the response.

    Args:
        study_id (str): The unique identifier of the study.
        model (str): The model to use for inference.
        prompt (str): The prompt to send to the model.
        timeout (int): The maximum time to wait for a response (in seconds).

    Returns:
        Optional[ModelResponse]: The model response if successful, otherwise None if timed out.
    """
    inference_id = self.prompt_model_async(study_id, model, prompt, response_format=response_format)
    return self.retrieve_prompt_response(study_id, inference_id, timeout)

  def prompt_model_async(
    self,
    study_id: str,
    model: str,
    prompt: str,
    nocache: bool = False,
    response_format: str = "text",
  ) -> str:
    """
    Prompts a model for inference asynchronously.

    Args:
        study_id (str): The unique identifier of the study.
        model (str): The model to use for inference.
        prompt (str): The prompt to send to the model.
        nocache (bool, optional): If True, bypasses the cache and generates a new response. Defaults to False.

    Returns:
        str: The unique identifier for the inference request.

    Raises:
        RuntimeError: If an unsuccessful response is received from the server.
    """
    response = requests.post(
      url=f"{self.base_url}/studies/{study_id}/inference",
      headers=self.default_headers,
      json={"model": model, "prompt": prompt, "nocache": nocache, "response_format": response_format},
    )
    if response.status_code != 202:
      raise RuntimeError(
        f"Received unsuccessful response while queuing inference.\nStatus code: {response.status_code} {response.text}"
      )
    return response.json()["id"]

  def retrieve_prompt_response(self, study_id: str, inference_id: str, timeout: int = 180) -> Optional[ModelResponse]:
    """
    Retrieves the response from a model inference request.

    Args:
        study_id (str): The unique identifier of the study.
        inference_id (str): The unique identifier of the inference request.
        timeout (int): The maximum time to wait for a response (in seconds).

    Returns:
        Optional[ModelResponse]: The model response if successful, otherwise None if timed out.

    Raises:
        RuntimeError: If an unsuccessful response is received from the server.
    """
    start = time.time()
    while True:
      response = requests.get(
        url=f"{self.base_url}/studies/{study_id}/inference/{inference_id}",
        headers=self.default_headers,
      )
      if response.status_code == 200:
        return self.__response_from_json(response.json())
      elif response.status_code != 404:
        raise RuntimeError(
          f"""Received unsuccessful response while retrieving model response.
          Status code: {response.status_code}, {response.text}"""
        )
      if time.time() - start >= timeout:
        return None

  def __study_from_json(self, json: dict) -> Study:
    images = []
    if "images" in json:
      for image in json["images"]:
        images.append(self.__image_from_json(image))

    return Study(id=json["id"], reference=json["reference"], images=images)

  def __studies_from_json(self, json: list) -> list[Study]:
    studies = []
    for study in json:
      studies.append(self.__study_from_json(study))
    return studies

  def __image_from_json(self, json: dict) -> Image:
    return Image(
      id=json["id"],
      reference=json["reference"],
      deidentified=json["deidentified"],
      uploaded=json["uploaded"],
    )

  def __response_from_json(self, json: dict) -> ModelResponse:
    return ModelResponse(success=json["success"], response=json["response"])

  def get_datasets(self) -> list[dict]:
    response = requests.get(f"{self.base_url}/datasets", headers=self.default_headers)
    if response.status_code != 200:
      raise RuntimeError(f"Failed to retrieve datasets: {response.status_code}, {response.text}")
    return response.json()

  def get_dataset(self, dataset_id: str) -> dict:
    response = requests.get(f"{self.base_url}/datasets/{dataset_id}", headers=self.default_headers)
    if response.status_code != 200:
      raise RuntimeError(f"Failed to retrieve dataset: {response.status_code}, {response.text}")
    return response.json()

  def create_dataset(self, name: str, description: str, file_path: str) -> dict:
    with open(file_path, "rb") as f:
      files = {"file": (os.path.basename(file_path), f, "application/jsonl")}
      data = {"name": name, "description": description}
      headers = {"x-api-key": self.default_headers["x-api-key"]}  # override content-type
      response = requests.post(f"{self.base_url}/datasets", headers=headers, files=files, data=data)
    if response.status_code != 201:
      raise RuntimeError(f"Failed to create dataset: {response.status_code}, {response.text}")
    return response.json()

  def get_dataset_status(self, dataset_id: str) -> DatasetStatus:
    response = requests.get(
      url=f"{self.base_url}/datasets/{dataset_id}/status",
      headers=self.default_headers,
    )

    if response.status_code != 200:
      raise RuntimeError(f"Failed to retrieve dataset status: {response.status_code}, {response.text}")
    return self.__dataset_status_from_json(response.json())

  def __dataset_status_from_json(self, json: dict) -> DatasetStatus:
    return DatasetStatus(
      total_images=json["total_images"], invalid_count=json["invalid_count"], deided_count=json["deided_count"]
    )

  def create_training_job(self, training_job: dict) -> dict:
    response = requests.post(
      f"{self.base_url}/training",
      headers=self.default_headers,
      json=training_job,
    )
    if response.status_code != 201:
      raise RuntimeError(f"Failed to create training job: {response.status_code}, {response.text}")
    return response.json()

  def get_training_job(self, training_job_id: str) -> dict:
    response = requests.get(f"{self.base_url}/training/{training_job_id}", headers=self.default_headers)
    if response.status_code != 200:
      raise RuntimeError(f"Failed to get training job: {response.status_code}, {response.text}")
    return response.json()

  def cancel_training_job(self, training_job_id: str) -> dict:
    response = requests.delete(f"{self.base_url}/training/{training_job_id}", headers=self.default_headers)
    if response.status_code != 200:
      raise RuntimeError(f"Failed to cancel training job: {response.status_code}, {response.text}")
    return response.json()
