rm -rf media
manim -pqh ./scripts/vis/manim.py ThreeDAxesScene # --> this will generate a new ./media file
# If a media folder exists within ./results/other replace it with the new ./media
rm -rf ./results/other/media
mv media ./results/other/