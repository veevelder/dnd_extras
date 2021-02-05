(async () => {
	const raven_name = "Royal";
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
		let item = token.actor.effects.find(a => a.data.label == "Sentinel Raven");

		if (item.data.disabled === false) {
			//raven is on token set raven to flying
			await token.actor.updateEmbeddedEntity("ActiveEffect", {"_id": item.data._id,  "disabled" : true});
			await Summoner.placeAndSummon(
			  token.actor,
			  raven_name,
			);
			// Update Token
			token.update({
				vision: true,
				dimSight: 0,
				brightSight: 0,
				dimLight: 0,
				brightLight:  0,
				lightAngle: 360
			});
			ChatMessage.create({content: `${token.actor.name}'s raven ${raven_name} now flies freely`})
		}
		else if (item.data.disabled === true){
			//raven is flying have it mount back on player find all just in case
			await token.actor.updateEmbeddedEntity("ActiveEffect", {"_id": item.data._id,  "disabled" : false});
			await Summoner.dismiss("Royal");
			//update token
			token.update({
				vision: true,
				dimSight: 30,
				brightSight: 0,
				dimLight: 0,
				brightLight:  0,
				lightAngle: 360
			});	
			ChatMessage.create({content: `${token.actor.name}'s raven ${raven_name} now sits on thier shoulder`})
		}
	}
	else {
		return ui.notifications.error("No Token Selected");
	}
})();