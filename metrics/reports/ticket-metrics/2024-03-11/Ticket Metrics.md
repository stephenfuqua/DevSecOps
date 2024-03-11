# Tech Team Ticket Metrics


```python
# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_tech_metrics.settings import load_from_env
from edfi_tech_metrics.jira import JiraBrowser
from edfi_tech_metrics.ticket_age import build_report_components

conf = load_from_env()
#conf.log_level = "DEBUG"
browser = JiraBrowser(conf)

portfolios = {
    "ODS Platform": ["ODS"],
    "Team B": ["METAED", "DMS", "ADMINAPI"],
    "Ed-Fi Tools": ["AA", "AC", "APIPUB", "DI", "EPPETA"],
    "Data Standard": [ "DATASTD", "MODL", "TPDMDEV"],
    "Support": ["EDFI"]
}

# DSOPS and TPDMX appear to be unused, removing those from Data Standard

projects = [i for _, v in portfolios.items() for i in v]
df = browser.get_unresolved_tickets(projects)
```

    [34mConnecting to https://tracker.ed-fi.org[0m
    [34mRetrieving tickets for ODS[0m
    [34mRetrieving tickets for METAED[0m
    [34mRetrieving tickets for DMS[0m
    [34mRetrieving tickets for ADMINAPI[0m
    [34mRetrieving tickets for AA[0m
    [34mRetrieving tickets for AC[0m
    [34mRetrieving tickets for APIPUB[0m
    [34mRetrieving tickets for DI[0m
    [34mRetrieving tickets for EPPETA[0m
    [34mRetrieving tickets for DATASTD[0m
    [34mRetrieving tickets for MODL[0m
    [34mRetrieving tickets for TPDMDEV[0m
    [34mRetrieving tickets for EDFI[0m
    

## Ticket Age


```python
stats = build_report_components(projects, df)
for s in stats:
    s.histogram.show()
```


    
![png](output_3_0.png)
    



    
![png](output_3_1.png)
    



    
![png](output_3_2.png)
    



    
![png](output_3_3.png)
    



    
![png](output_3_4.png)
    



    
![png](output_3_5.png)
    



    
![png](output_3_6.png)
    



    
![png](output_3_7.png)
    



    
![png](output_3_8.png)
    



    
![png](output_3_9.png)
    



    
![png](output_3_10.png)
    



    
![png](output_3_11.png)
    



    
![png](output_3_12.png)
    



```python
import pandas as pd
from datetime import datetime

stats_df = pd.concat([s.stats for s in stats])

today = datetime.today().strftime('%Y-%m-%d')

stats_df["date"] = today
stats_df.reset_index(inplace=True)
stats_df.rename(columns={"index": "project"}, inplace=True)

from pathlib import Path
Path("./data/ticket-age").mkdir(parents=True, exist_ok=True)

file_name = f"./data/ticket-age/{today}.csv"
conf.info(f"Writing age data out to file: {file_name}")
stats_df.to_csv(file_name)

stats_df
```

    [34mWriting age data out to file: ./data/ticket-age/2024-03-11.csv[0m
    




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>project</th>
      <th>count</th>
      <th>mean</th>
      <th>std</th>
      <th>min</th>
      <th>25%</th>
      <th>50%</th>
      <th>75%</th>
      <th>max</th>
      <th>date</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>ODS</td>
      <td>357.0</td>
      <td>936.081232</td>
      <td>777.106081</td>
      <td>0.0</td>
      <td>81.00</td>
      <td>868.0</td>
      <td>1692.0</td>
      <td>2875.0</td>
      <td>2024-03-11</td>
    </tr>
    <tr>
      <th>1</th>
      <td>METAED</td>
      <td>148.0</td>
      <td>1218.831081</td>
      <td>1112.465854</td>
      <td>4.0</td>
      <td>370.00</td>
      <td>555.0</td>
      <td>2070.0</td>
      <td>3188.0</td>
      <td>2024-03-11</td>
    </tr>
    <tr>
      <th>2</th>
      <td>DMS</td>
      <td>24.0</td>
      <td>20.666667</td>
      <td>12.239163</td>
      <td>3.0</td>
      <td>11.00</td>
      <td>21.0</td>
      <td>31.5</td>
      <td>54.0</td>
      <td>2024-03-11</td>
    </tr>
    <tr>
      <th>3</th>
      <td>ADMINAPI</td>
      <td>568.0</td>
      <td>180.927817</td>
      <td>66.365936</td>
      <td>17.0</td>
      <td>103.00</td>
      <td>209.0</td>
      <td>223.0</td>
      <td>528.0</td>
      <td>2024-03-11</td>
    </tr>
    <tr>
      <th>4</th>
      <td>AA</td>
      <td>105.0</td>
      <td>708.657143</td>
      <td>440.328239</td>
      <td>66.0</td>
      <td>312.00</td>
      <td>551.0</td>
      <td>1085.0</td>
      <td>1841.0</td>
      <td>2024-03-11</td>
    </tr>
    <tr>
      <th>5</th>
      <td>AC</td>
      <td>11.0</td>
      <td>20.727273</td>
      <td>6.214353</td>
      <td>11.0</td>
      <td>16.00</td>
      <td>24.0</td>
      <td>26.0</td>
      <td>26.0</td>
      <td>2024-03-11</td>
    </tr>
    <tr>
      <th>6</th>
      <td>APIPUB</td>
      <td>15.0</td>
      <td>126.133333</td>
      <td>113.424529</td>
      <td>5.0</td>
      <td>12.00</td>
      <td>96.0</td>
      <td>198.5</td>
      <td>328.0</td>
      <td>2024-03-11</td>
    </tr>
    <tr>
      <th>7</th>
      <td>DI</td>
      <td>105.0</td>
      <td>809.095238</td>
      <td>513.914549</td>
      <td>13.0</td>
      <td>376.00</td>
      <td>717.0</td>
      <td>1106.0</td>
      <td>1837.0</td>
      <td>2024-03-11</td>
    </tr>
    <tr>
      <th>8</th>
      <td>EPPETA</td>
      <td>24.0</td>
      <td>117.750000</td>
      <td>89.983694</td>
      <td>33.0</td>
      <td>39.00</td>
      <td>80.5</td>
      <td>202.0</td>
      <td>273.0</td>
      <td>2024-03-11</td>
    </tr>
    <tr>
      <th>9</th>
      <td>DATASTD</td>
      <td>518.0</td>
      <td>1780.444015</td>
      <td>912.758310</td>
      <td>11.0</td>
      <td>1181.00</td>
      <td>1942.0</td>
      <td>2319.0</td>
      <td>4067.0</td>
      <td>2024-03-11</td>
    </tr>
    <tr>
      <th>10</th>
      <td>MODL</td>
      <td>272.0</td>
      <td>2042.143382</td>
      <td>599.095177</td>
      <td>427.0</td>
      <td>1701.00</td>
      <td>2200.0</td>
      <td>2516.5</td>
      <td>2699.0</td>
      <td>2024-03-11</td>
    </tr>
    <tr>
      <th>11</th>
      <td>TPDMDEV</td>
      <td>28.0</td>
      <td>771.821429</td>
      <td>410.893070</td>
      <td>68.0</td>
      <td>375.25</td>
      <td>928.0</td>
      <td>1133.0</td>
      <td>1329.0</td>
      <td>2024-03-11</td>
    </tr>
    <tr>
      <th>12</th>
      <td>EDFI</td>
      <td>141.0</td>
      <td>467.602837</td>
      <td>210.207003</td>
      <td>5.0</td>
      <td>375.00</td>
      <td>537.0</td>
      <td>644.0</td>
      <td>685.0</td>
      <td>2024-03-11</td>
    </tr>
  </tbody>
</table>
</div>



## Backlog Health

Enter current team average velocity over the last five sprints below:


```python
import ipywidgets as widgets
from IPython.display import display, Markdown
import pandas as pd

def get_portfolio_health(team: str, velocity: int):
    total_points = df[df["project"].isin(portfolios[team])].points.sum()

    return { 
        "points": total_points,
        "velocity": velocity,
        "health": round(total_points/velocity)
    }

df_health = None
def build_health_report(data_standard, edfi_tools, ods_platform, team_b):
    global df_health
    ds_v = float(data_standard)
    tools_v = float(edfi_tools)
    ods_v = float(ods_platform)
    b_v = float(team_b)

    health = {}
    health["Data Standard"] = get_portfolio_health("Data Standard", ds_v)
    health["Ed-Fi Tools"] = get_portfolio_health("Ed-Fi Tools", tools_v)
    health["ODS Platform"] = get_portfolio_health("ODS Platform", ods_v)
    health["Team B"] = get_portfolio_health("Team B", b_v)
    
    df_health = pd.DataFrame(health).transpose()

# Default to 1.0 to avoid temporary divide by zero
_ = widgets.interact_manual(build_health_report, data_standard="1.0", edfi_tools="1.0", ods_platform="1.0", team_b="1.0")
```


    interactive(children=(Text(value='1.0', continuous_update=False, description='data_standard'), Text(value='1.0…





```python
display(df_health)

path = "./data/backlog-health"
Path(path).mkdir(parents=True, exist_ok=True)

file_name = f"{path}/{today}.csv"
conf.info(f"Writing health data out to file: {file_name}")
df_health.to_csv(file_name)
```


<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>points</th>
      <th>velocity</th>
      <th>health</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>Data Standard</th>
      <td>53.0</td>
      <td>24.75</td>
      <td>2.0</td>
    </tr>
    <tr>
      <th>Ed-Fi Tools</th>
      <td>266.0</td>
      <td>28.00</td>
      <td>10.0</td>
    </tr>
    <tr>
      <th>ODS Platform</th>
      <td>193.5</td>
      <td>19.71</td>
      <td>10.0</td>
    </tr>
    <tr>
      <th>Team B</th>
      <td>153.0</td>
      <td>23.50</td>
      <td>7.0</td>
    </tr>
  </tbody>
</table>
</div>


    [34mWriting health data out to file: ./data/backlog-health/2024-03-11.csv[0m
    

## Todo

Account for fixed version.

* Should we only care about age for things that are not assigned to a version? That gets to the real concern.
* If so, that would be easy to game, with a fake fixed version (like "backlog" in MetaEd)
* Should the health only look at items that are in fixed versions? The _next_ version perhaps?
