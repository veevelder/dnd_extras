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
		let effect = token.actor.effects.find(a => a.data.label == "Mage Hand");

		if (effect.data.disabled === false) {
			//mage hand is cast
			let item = token.actor.items.find(a => a.name == "Mage Hand");
			await token.actor.updateEmbeddedEntity("ActiveEffect", {"_id": effect.data._id,  "disabled" : true});
			await Summoner.placeAndSummonFromSpell(token.actor, item, "Mage Hand");
			ChatMessage.create({content: `${token.actor.name} makes a spectral, floating hand appear!`})
		}
		else if (effect.data.disabled === true){
			//raven is flying have it mount back on player find all just in case
			await token.actor.updateEmbeddedEntity("ActiveEffect", {"_id": effect.data._id,  "disabled" : false});
			await Summoner.dismiss("Mage Hand");
			ChatMessage.create({content: `${token.actor.name}'s makes the spectral, floating hand disappear!`})
		}
	}
	else {
		return ui.notifications.error("No Token Selected");
	}
})();