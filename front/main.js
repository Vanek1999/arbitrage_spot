window.onload = init;

async function updatePairs(){
	deposit = prompt("Ваш депозит в $ ");
	document.getElementById("bitcoin").removeAttribute("style");
	newPairs = await eel.test(deposit)();
	document.getElementById("bitcoin").setAttribute("style", "opacity:0");


	table = document.createElement("table");
	table.id = 'table_pairs';
	table.innerHTML = '<tr id="tr_pairs"></tr>';
	document.getElementById("mainContent").appendChild(table);

	document.getElementById("rightCalc").removeAttribute("style");
	document.getElementById("mainContent").removeAttribute("style");
	document.getElementById("flex").removeAttribute("style");

	while (true){
		//document.location.reload();
		document.getElementById("deposit").value = deposit;
		numElem = 0
		var trId = "tr_pairs";
		document.querySelector('table').remove();
		table = document.createElement("table");
		table.id = 'table_pairs';
		table.innerHTML = '<tr id="tr_pairs"></tr>';
		document.getElementById("mainContent").appendChild(table);
		for (let i = 1; ; i++){
			if (newPairs.split("\n")[i] == undefined){break}

			if (numElem <= 6){
				newElement = document.createElement("td");
				newElement.innerHTML = '<div class="pair" onclick="handleButtonPairClick(this.innerHTML)">' + newPairs.split("\n")[i] + '</div>';
				document.getElementById(trId).appendChild(newElement);
				numElem++;
			}
			else{
				numElem = 0;
				tr = document.getElementById(trId);
				trId = "tr_pairs" + i;
				tr.insertAdjacentHTML("afterEnd", '<tr id="' + trId +'"></tr>');
				newElement = document.createElement("td");
				newElement.innerHTML = '<div class="pair" onclick="handleButtonPairClick(this.innerHTML)">' + newPairs.split("\n")[i] + '</div>';
				document.getElementById(trId).appendChild(newElement);
				numElem++;
			}
		}
		newPairs = await eel.test(deposit)();
	}
}

updatePairs();

function init(){
    document.getElementById("button").onclick = handleButtonClick;
}

function handleButtonClick() {
	deposit = document.getElementById("deposit").value;
	price_1 = document.getElementById("price_1").value;
	price_2 = document.getElementById("price_2").value;
	fee_procent = document.getElementById("fee_procent").value;
	fee_dollars = document.getElementById("fee_dollars").value;

	amount_coin = deposit / price_1 * price_2;
	fee_procent = fee_procent / 100;
	procent = amount_coin - amount_coin * fee_procent - fee_dollars;
	if (procent > deposit){
		alert('Связка валидная!\nЧистый процент: ' + ((procent-deposit) / document.getElementById("deposit").value * 100).toFixed(3) + "%\nЧистые $" + (procent-deposit).toFixed(3));
	}
	else{
		alert("Связка не валидная!");
	}
}

function handleButtonPairClick(pair_info) {
	prices = pair_info.split("<br>")[2];
	document.querySelector('#price_1').value = prices.split("➡")[0];
	document.querySelector('#price_2').value = prices.split("➡")[1];
	document.querySelector('#coin').value = pair_info.split(" ")[1].split("<br>")[0];
	document.querySelector('#exchange').value = pair_info.split("<br>")[1].split("<br>")[0];
}

