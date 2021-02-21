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
		let effect = token.actor.effects.find(a => a.data.label == "Spiritual Weapon");

		if (effect.data.disabled === false) {
			//Spiritual Weapon is cast
			let item = token.actor.items.find(a => a.name == "Spiritual Weapon");
			await token.actor.updateEmbeddedEntity("ActiveEffect", {"_id": effect.data._id,  "disabled" : true});
			await Summoner.placeAndSummonFromSpell(token.actor, item, "Spiritual Weapon");
			ChatMessage.create({content: `${token.actor.name} summons a mighty Spiritual Weapon!`})
		}
		else if (effect.data.disabled === true){
			//Spiritual Weapon is unsummoned
			await token.actor.updateEmbeddedEntity("ActiveEffect", {"_id": effect.data._id,  "disabled" : false});
			await Summoner.dismiss("Spiritual Weapon");
			ChatMessage.create({content: `${token.actor.name}'s makes the Spiritual Weapon disappear!`})
		}
	}
	else {
		return ui.notifications.error("No Token Selected");
	}
})();