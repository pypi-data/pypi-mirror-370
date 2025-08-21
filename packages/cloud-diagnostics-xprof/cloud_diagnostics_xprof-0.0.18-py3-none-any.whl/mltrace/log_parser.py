# Copyright 2023 Google LLC
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#      https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Parser for the logs that filters, groups and enriches the logs."""

import pandas as pd
from mltrace import constants


def parse_mcjax(logs: pd.DataFrame, jobname: str) -> pd.DataFrame:
  """Parses, groups and enriches MCJAX workload logs.

  Args:
      logs (pd.DataFrame): Workload logs
      jobname (str): Name of the workload

  Returns:
      pd.DataFrame: Enriched logs
  """
  logs["worker_num"] = logs["resource.labels.pod_name"].str.extract(
      rf"{jobname}-.*?-(\d*?-\d*?)-"
  )
  logs["podtype"] = constants.WORKER_GROUP_PREFIX + logs["worker_num"]
  # slice#0 worker#0 is the Coordinator.
  logs.loc[
      logs["podtype"] == constants.WORKER_GROUP_PREFIX + "0-0", "podtype"
  ] = "Coordinator"

  return logs


def parse_pathways(logs: pd.DataFrame) -> pd.DataFrame:
  """Parses, groups and enriches Pathways workload logs.

  Args:
      logs (pd.DataFrame): Workload logs

  Returns:
      pd.DataFrame: Enriched logs
  """
  logs.loc[logs["podtype"] == "rm", "podtype"] = "Resource Manager"

  return logs


def add_section(logs: pd.DataFrame) -> pd.DataFrame:
  """Sub-group the logs.

  Args:
      logs (pd.DataFrame): Workload logs

  Returns:
      pd.DataFrame: Logs with a new "section" column
  """
  logs = logs.assign(section=logs["sourceLocation.file"])
  logs.loc[logs["section"].isna(), "section"] = "Other logs"
  logs.loc[logs["section"] == "", "section"] = "Other logs"
  for k in constants.REGEX_SUBSTR_MATCH_ROW_HEADERS:
    logs.loc[
        logs["textPayload"].str.contains(k, case=False, regex=True), "section"
    ] = constants.REGEX_SUBSTR_MATCH_ROW_HEADERS[k]

  return logs


def filter_out_unnecessary_logs(logs: pd.DataFrame) -> pd.DataFrame:
  """Remove the logs that are usually not helpful in debugging.

  Args:
      logs (pd.DataFrame): Workload logs

  Returns:
      pd.DataFrame: Filtered logs
  """
  logs = logs[~logs["textPayload"].isin(constants.REDUNDANT_LOGS_EXACT)]
  r = '|'.join(constants.REDUNDANT_LOGS_SUBSTR_MATCH)
  logs = logs[~logs["textPayload"].str.contains(r, regex=True)]
  for filename, severity in constants.REDUNDANT_SEVERITY_IN_FILES.items():
    logs = logs[
        ~(
            (logs["sourceLocation.file"] == filename)
            & (logs["severity"] == severity)
        )
    ]

  return logs


def parse_logs(logs: pd.DataFrame, jobname: str) -> pd.DataFrame:
  """Parses, groups and enriches the workload logs.

  Args:
      logs (pd.DataFrame): Workload logs
      jobname (str): Name of the workload

  Returns:
      pd.DataFrame: Enriched logs
  """
  if "resource" in logs.columns:
    logs["resource.labels.pod_name"] = logs["resource"].apply(
        lambda x: x.get("labels").get("pod_name")
    )
    logs["resource.labels.container_name"] = logs["resource"].apply(
        lambda x: x.get("labels").get("container_name")
    )
  logs["podtype"] = logs["resource.labels.pod_name"].str.extract(
      rf"{jobname}-(.*?)-"
  )
  # todo: Use a better way to identify the workload.
  if "slice" in logs["podtype"].values or "job" in logs["podtype"].values:
    logs = parse_mcjax(logs, jobname)
  else:
    logs["podtype"] = logs["resource.labels.container_name"]
    logs = parse_pathways(logs)

  if "jsonPayload" in logs.columns:
    logs["jsonPayload.message"] = logs["jsonPayload"].apply(
        lambda x: x.get("message") if not pd.isnull(x) else ""
    )
  logs["textPayload"] = logs["textPayload"].fillna(logs["jsonPayload.message"])
  logs.dropna(subset=["textPayload"], inplace=True)

  if "sourceLocation" in logs.columns:
    logs["sourceLocation.file"] = logs["sourceLocation"].apply(
        lambda x: x.get("file") if not pd.isnull(x) else ""
    )

  logs = filter_out_unnecessary_logs(logs)

  logs = add_section(logs)

  return logs
