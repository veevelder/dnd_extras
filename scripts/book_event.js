function book_show_page(e, l) {
	e.stopPropagation()
	$(".chapter-section").hide()
	let content = $($(l).attr('href'))
	content.find(".chapter-section").show()
	content.parents(".chapter-section").show()
	content.show()
}