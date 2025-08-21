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

"""run_mltrace.py converts GCP workload logs into a sequence of Traces.

The traces are grouped on multiple levels to make the logs easier to comprehend.
To run this script, use the command below.

python3 run_mltrace.py -f <json_or_csv_filepath> -j <jobset_name>

The output of the script will be a .gz filepath which stores the traces.
"""

from mltrace import main

if __name__ == "__main__":
  main.main()
