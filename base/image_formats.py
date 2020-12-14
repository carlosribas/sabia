from wagtail.images.formats import Format, register_image_format, unregister_image_format

unregister_image_format('fullwidth')
register_image_format(Format('fullwidth', 'Full width', 'richtext-image img-fluid', 'width-1100'))

unregister_image_format('left')
register_image_format(Format('left', 'Left-aligned', 'richtext-image img-fluid float-left mr-3', 'width-450'))

unregister_image_format('right')
register_image_format(Format('right', 'Right-aligned', 'richtext-image img-fluid float-right ml-3', 'width-450'))