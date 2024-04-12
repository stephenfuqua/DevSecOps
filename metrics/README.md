# Ed-Fi Tech Metrics

Jupyter notebooks and related code for calculating Ed-Fi tech team metrics.

## Use Instructions

Requires Python >= 3.10 and Poetry.

1. Create a `.env` file in the root project directory:

   ```none
   JIRA_TOKEN=<INSERT PERSONAL TOKEN FROM JIRA>
   JIRA_BASE_URL=https://tracker.ed-fi.org

   # Optional
   # LOG_LEVEL=<DEBUG,INFO,WARN,ERROR>
   # PAGE_SIZE=100
   ```

2. Install package dependencies: `poetry install`
3. Open the Jupyter Notebooks either:
   1. Directly in VS Code.
   2. Or from Jupyter server: `poetry run juypter lab` (newer UI) or `poetry run
      jupyter notebook` (original UI).
4. Run all cells

Some of these will generate CSV files in the `data` directory. These files can
be used to compare results over time. Go ahead and store them in a commit when
they are accurate and complete!

## Legal Information

Copyright (c) 2024 Ed-Fi Alliance, LLC and contributors.

Licensed under the [Apache License, Version 2.0](LICENSE) (the "License").

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

See [NOTICES](NOTICES.md) for additional copyright and license notifications.
