SET TARGET_DIR=C:\Users\kevin\Videos

SET date=%date:~4%
SET date=%date:/=-%
SET time=%time:~-0,-3%
SET time=%time::=%

scrcpy --video-codec=h265 --max-size=1920 --max-fps=120 --record=%TARGET_DIR%\%date%_at-%time%_scrcpy-recording.mp4 --record-format=mp4