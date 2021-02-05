(async () => {
	let token = null;
	if(game.user.isGM) {
		if(canvas.tokens.controlled.length > 1) {
			return ui.notifications.error("Only select one token at a time!");
		}
		else if(canvas.tokens.controlled.length == 0) {
			return ui.notifications.error("Must Select at least one token!");
		}
		else {
			token = canvas.tokens.controlled[0];
		}
	}
	else {
		token = canvas.tokens.placeables.filter(a => a.actor).find(a => a.actor._id == game.user.data.character)
	}
	
	if(token) {
		let item = token.actor.items.find(a => a.name == "Find Familiar");
		//check magic items
		if (!item) {
			if(MagicItems.actor(token.actor._id).items.find(a => a.spells.find(b => b.name == "Find Familiar"))) {
				item = true;
			}
		}
		
		if (item) {
			if (token.data.flags.hasOwnProperty("familiar") && token.data.flags["familiar"] != "") {
				//summoned familiar
				let d = Dialog.confirm({
					title: "Unsummon Familiar?",
					content: `<p>Do you want to Unsummon ${token.data.flags["familiar"]}?</p>`,
					yes: async () => {
						ChatMessage.create({content: `${token.data.flags["familiar"]} disapears`});
						await Summoner.dismiss(token.data.flags["familiar"]);
						token.update({
							flags: {"familiar": ""}
						})
					},
					defaultYes: false
				});
				
			}
			else {
				//no summoned familiar
				let familiars = game.folders.find(a => a.name == "Summons").content.filter(a => a.data.type == "npc").filter(a => a.data.data.details.type == "Beast").map(a => a.name);
				let applyChanges = false;
				new Dialog({
				  title: "Find Familiar",
				  content: `<form>
					  <div class="form-group">
						<label>Familiar</label>
						<select id="familiar" name="familiar">
						  ${
							familiars.map(function(familiar, index) {
								return `<option value="${familiar}">${familiar}</option>`;
							}).join('\n')
						  }
						</select>
					  </div>
					</form>`,
					buttons: {
						yes: {
							icon: "<i class='fas fa-check'></i>",
							label: "Summon",
							callback: () => applyChanges = true
						},
						no: {
							icon: "<i class='fas fa-times'></i>",
							label: "Cancel"
						},
					},
					default: "yes",
					close: async html => {
						if (applyChanges) {
							let familiar = html.find('[name="familiar"]')[0].value;
							token.update({
								flags: {"familiar": familiar}
							})
							if (typeof item == "boolean") {
								Summoner.placeAndSummon(token.actor, familiar);
							}
							else {
								Summoner.placeAndSummonFromSpell(token.actor, item, familiar);
							}
							ChatMessage.create({content: `${familiar} has been summoned`});
						}
					}
				}).render(true);				
			}
		}
		else {
			return ui.notifications.error(`${token.actor.name} does not have the spell Find Familiar`);
		}
	}
	else {
		return ui.notifications.error("No Token Selected");
	}
})();