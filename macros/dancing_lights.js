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
		let effect = token.actor.effects.find(a => a.data.label == "Dancing Lights");

		if (effect.data.disabled === false) {
			//Dancing Lights is cast
			let item = token.actor.items.find(a => a.name == "Dancing Lights");
			await token.actor.updateEmbeddedEntity("ActiveEffect", {"_id": effect.data._id,  "disabled" : true});
			await Summoner.placeAndSummonFromSpell(token.actor, item, "Meara's Dancing Light");
			ChatMessage.create({content: `${token.actor.name} makes a sphere of glowing light appear!`})
		}
		else if (effect.data.disabled === true){
			//Dancing Lights is unsummoned
			await token.actor.updateEmbeddedEntity("ActiveEffect", {"_id": effect.data._id,  "disabled" : false});
			await Summoner.dismiss("Meara's Dancing Light");
			ChatMessage.create({content: `${token.actor.name}'s makes the sphere of glowing light disappear!`})
		}
	}
	else {
		return ui.notifications.error("No Token Selected");
	}
})();