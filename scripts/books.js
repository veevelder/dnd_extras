class PHB extends Application {
	constructor(options) {
		super(options);
		this.chapters = []
	}
	
	static get defaultOptions() {
		const options = super.defaultOptions;
		options.template = "modules/dnd-extras/templates/phb.html";
		options.width = 1200;
		options.height = 700;
		options.resizable = true;
		options.class = ["phb-book"];
		options.title = "Player's Handbook";
		return options
	}
	
	async loadChapters() {
		console.log('Books | Starting to load Player Handbook folder data');
		let response = await fetch('modules/dnd-extras/books/phb-folders.db');
		if(!response.ok) {
			console.error(response);
			throw Error('Books | Failed to load Player Handbook folder data.')
			return;
		}
		let ch = await response.text()
		ch = ch.split("\n")
		for(var i = 0; i < ch.length; i++) {
			if (ch[i] == "") {
				break;
			}
			let tmp = JSON.parse(ch[i])
			tmp.subchapters = []
			if (tmp.parent == null) {
				this.chapters.push(tmp)
			}
			else {
				let parent = this.chapters.filter(a => a._id == tmp.parent)[0]
				parent.subchapters.push(tmp)
				parent.subchapters.sort(function(a, b) {
					if(a.sort < b.sort) {
						return -1;
					}
					else if(a.sort > b.sort) {
						return 1;
					}
					return 0;
				});
			}
		}
		//sort chapters
		this.chapters.sort(function(a, b) {
			if(a.sort < b.sort) {
				return -1;
			}
			else if(a.sort > b.sort) {
				return 1;
			}
			return 0;
		});
	}
	
	async loadContent() {
		let pack = game.packs.get("dnd-extras.phb");
		await pack.getIndex();
		for(var i = 0; i < pack.index.length; i++) {
			let content = await pack.getEntity(pack.index[i]._id);
			if(content.data.folder == null) {
				console.log("Books | PHB content has no parent", content)
			}
			else {
				let parent = this.chapters.filter(a => a._id == content.data.folder)
				if (parent.length == 0) {
					for(var j = 0; j < this.chapters.length; j++) {
						parent = this.chapters[j].subchapters.filter(a => a._id == content.data.folder)
						if(parent.length != 0) {
							break
						}
					}
				}
				parent[0].subchapters.push(content)
				parent[0].subchapters.sort(function(a, b) {
					if(a.sort < b.sort) {
						return -1;
					}
					else if(a.sort > b.sort) {
						return 1;
					}
					return 0;
				});
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
			let win = new PHB(PHB.defaultOptions);
			await win.loadChapters();
			await win.loadContent();
			win.render(true);
		})
		html.find(".directory-footer").append(button);
	}
})