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
		let effect = token.actor.effects.find(a => a.data.label == "Squirrel (Mage) Hand");
		console.log(effect)
		if (effect.data.disabled === false) {
			//Squirrel hand is cast
			let item = token.actor.items.find(a => a.name == "Squirrel (Mage) Hand");
			await token.actor.updateEmbeddedEntity("ActiveEffect", {"_id": effect.data._id,  "disabled" : true});
			await Summoner.placeAndSummonFromSpell(token.actor, item, "Squirrel Hand");
			ChatMessage.create({content: `${token.actor.name} makes a spectral, floating hand made of squirrels appear!`})
		}
		else if (effect.data.disabled === true){
			//Squirrel hand is dissmissed
			await token.actor.updateEmbeddedEntity("ActiveEffect", {"_id": effect.data._id,  "disabled" : false});
			await Summoner.dismiss("Squirrel Hand");
			ChatMessage.create({content: `${token.actor.name}'s makes the spectral, floating hand made of squirrels disappear!`})
		}
	}
	else {
		return ui.notifications.error("No Token Selected");
	}
})();