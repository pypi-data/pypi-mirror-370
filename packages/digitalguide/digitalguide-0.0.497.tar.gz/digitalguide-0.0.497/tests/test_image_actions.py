from PIL import Image
from digitalguide.special_actions.imageActions import overlay_images
import pytest

@pytest.mark.parametrize("ratio", [
    (4096, 3072),
    (3072, 4096)
])
def test_overlay_images(ratio):

    im = overlay_images(Image.new(mode="RGBA", size=ratio, color="blue"), Image.open("./tests/assets/foreground.png"),  x_position="right", y_position="bottom", resize=True)
    assert_image_equal_tofile(im, "./tests/assets/result_{}_{}.png".format(ratio[0], ratio[1]))
    # Write the stuff
    # im.save("result_{}_{}.png".format(ratio[0], ratio[1]))

def assert_image_equal(a, b, msg=None):
    assert a.mode == b.mode, msg or f"got mode {repr(a.mode)}, expected {repr(b.mode)}"
    assert a.size == b.size, msg or f"got size {repr(a.size)}, expected {repr(b.size)}"
    assert a.tobytes() == b.tobytes(), msg or "got different content"

def assert_image_equal_tofile(a, filename, msg=None, mode=None):
    with Image.open(filename) as img:
        if mode:
            img = img.convert(mode)
        assert_image_equal(a, img, msg)