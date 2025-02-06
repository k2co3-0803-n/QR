def scanQR():
	print("お手持ちのQRコードをリーダにかざして下さい．")
	informations = input().split("/")
	# while True:
		# information = input()
		# if (information == ""):
			# break
		# informations.append(information)
	
	print(f"読み取った情報：{informations}")
	affiliation = informations[0]
	year = informations[1]
	name = informations[2]
	return affiliation, year, name
