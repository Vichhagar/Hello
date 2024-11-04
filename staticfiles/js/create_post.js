let image_template = `
    <div class="post_image">
        <label class="image_input">
            <input type="file" hidden name="post_image" class="post_image_input" onchange="update_image_preview(this)">
            <div class="preview_area">
                <img id="add_new_image_icon" src="/static/img/add_image.png" alt="">
            </div>
        </label>
    </div>
`;

const update_image_preview = (e) => {
    let post_images_preview = document.getElementById('post_images_preview')

    let preview_area = e.nextElementSibling;
    let existing_img = document.getElementById('add_new_image_icon');

    const tempContainer = document.createElement('div');
    tempContainer.innerHTML = image_template;

    post_images_preview.appendChild(tempContainer)
    let img_src = URL.createObjectURL(e.files[0])
    let new_img = document.createElement('img');
    new_img.src = img_src;
    preview_area.replaceChild(new_img, existing_img);
}