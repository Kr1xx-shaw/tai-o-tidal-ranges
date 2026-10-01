# Process

## Tools

I used Codex to read the assignment template, explore possible datasets, write most of the Python code, draft the documentation and check the results. Early daylight concepts used AI image generation, but the final tide picture is drawn by Python and Matplotlib from the saved HKO file. The interactive companion embeds a Matplotlib 3D canvas in a native Qt window using PySide6 Essentials. Its dependency block lets uv install both plotting and window libraries. The course's circular tide example informed the angle-and-radius approach; this project uses Tai O and daily ranges across twelve months instead of the classroom's Quarry Bay hourly chart.

I directed the visual changes: three separate months became one overlaid chart, then six months, then a full year. I requested muted blue-green, pink and yellow colours, retained orange maximum markers, and added black minimum markers. After comparing a flat image with a 45-degree perspective, I selected the flat image for the PNG. I later requested a separate interactive 45-degree view with a vertical slider to spread the monthly layers, and reviewed a static preview before asking for it to be added. Codex checked all 365 dates and 8,760 hourly values and compared the saved JSON values with a fresh official CSV download; the fields and values matched.

## Kept

I kept a shared radius scale and a fixed 31-position angular scale because the same calendar day should occupy the same angle in every month. I also kept light transparent fills and monthly maximum and minimum markers. In the interactive version, the slider changes only vertical display offsets, so it does not alter dates or daily ranges. Hovering a point shows its date, range and two hourly extrema in the side panel; month toggles help inspect one layer. Raw data stays unchanged and both outputs use the same validation and radius calculation. The desktop window reads the committed data offline after uv has installed the declared dependencies. The static PNG remains the picture embedded in the README.

## Rejected

I rejected the dense annual daylight stripe plot and the AI-generated daylight rings, which made the months look nearly identical. I rejected perspective as a replacement for the flat PNG because it changes apparent distances; it now serves as an optional interactive companion, with a top-view control and exact values on hover. I also rejected the initial HTML delivery because opening it was inconvenient: I requested a native window launched directly by uv, and Codex replaced the browser implementation and removed its HTML output. During the data review, the broad label "daily tidal range" was refined to "range of hourly tide predictions": hourly sampling can miss the exact high and low water between samples. Month-end joins are dashed and explained as graphical closures, not measurements. The final scripts validate dates and values and fail visibly instead of silently discarding unparseable rows.
