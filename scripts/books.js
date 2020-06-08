async function find_chapter(chapters, item) {
	for(var i = 0; i < chapters.length; i++) {
		if(chapters[i].data._id == item.data.folder) {
			chapters[i].subchapters.push(item)
		}
		else if(chapters[i].subchapters.length > 0) {
			await find_chapter(chapters[i].subchapters, item)
		}
	}
}

class PlayersHandbook extends Application {
	constructor(options) {
		super(options);
		this.chapters = []
	}
	
	static get defaultOptions() {
		const options = super.defaultOptions;
		options.template = "modules/dnd-extras/templates/phb.html";
		options.width = 1200;
		options.height = 800;
		options.resizable = true;
		options.class = ["phb-book"];
		options.title = "Player's Handbook";
		return options
	}
	
	async loadContent() {
		//loop through all packs to load them
		let pack = null;
		for (var i = 0; i < game.packs.entries.length; i++) {
			let tmpPack = game.packs.get(game.packs.entries[i].collection)
			await tmpPack.getIndex();
			if(game.packs.entries[i].collection == "dnd-extras.phb") {
				pack = tmpPack;
			}
		}
		let tmpChapters = []
		for(var i = 0; i < pack.index.length; i++) {
			tmpChapters.push(await pack.getEntity(pack.index[i]._id));
		}
		tmpChapters.sort((a,b) => a.data.sort - b.data.sort);
		for(var i = 0; i < tmpChapters.length; i++) {
			tmpChapters[i].subchapters = []
			tmpChapters[i].data.content = await TextEditor.enrichHTML(tmpChapters[i].data.content)
			if (tmpChapters[i].data.folder == "") {
				this.chapters.push(tmpChapters[i])
			}
			else {
				await find_chapter(this.chapters, tmpChapters[i])
			}
		}
	}
	
	getData() {
		let data = {
			data: this.data
		};
		data.chapters = this.chapters
		return data;
	}
}

Hooks.on("renderSidebarTab", async (app, html) => {
	if(app.options.id == "journal") {
		let button = $("<button class='view-phb'><i class='fas fa-book'></i> Player's Handbook</button>")
		button.click(async function() {
			//create a new window			
			let win = new PlayersHandbook(PlayersHandbook.defaultOptions);
			await win.loadContent();
			win.render(true);
		})
		html.find(".directory-footer").append(button);
	}
})