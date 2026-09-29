# Process

## Tools

I used Codex to read the assignment template, explore possible datasets, write most of the Python code, draft the documentation and check the results. Early daylight concepts used AI image generation, but the final tide picture is drawn by Python and Matplotlib from the saved HKO file. The course's circular tide example informed the angle-and-radius approach; this project uses Tai O and daily ranges across twelve months instead of the classroom's Quarry Bay hourly chart.

I directed the visual changes: three separate months became one overlaid chart, then six months, then a full year. I requested muted blue-green, pink and yellow colours and retained orange maximum markers. After comparing a flat image with a 45-degree perspective, I selected the flat image. Codex checked all 365 dates and 8,760 hourly values and compared the saved JSON values with a fresh official CSV download; the fields and values matched.

## Kept

I kept a shared radius scale and a fixed 31-position angular scale because the same calendar day should occupy the same angle in every month. I also kept light transparent fills and monthly maximum markers: they support the layered appearance while leaving individual outlines visible. Raw data stays unchanged; parsing and arithmetic happen in the plotting script, which does not access the network.

## Rejected

I rejected the dense annual daylight stripe plot and the AI-generated daylight rings, which made the months look nearly identical. I also rejected the perspective view for the final submission because it changes apparent distances. During the data review, the broad label "daily tidal range" was refined to "range of hourly tide predictions": hourly sampling can miss the exact high and low water between samples. Month-end joins are dashed and explained as graphical closures, not measurements. The final scripts validate dates and values and fail visibly instead of silently discarding unparseable rows.
