def count_letters(word):
    count = 0
    for ch in word:
        if ch.isalpha():  
            count += 1
    return count

while True:
    print("----- How many letters are in a word -----")
    w = str(input("Enter your word: ")).strip()

    # Empty input
    if not w:
        print("❌ Please enter a word!")

    # Numbers or symbols not allowed
    elif not w.isalpha():
        print("❌ Numbers and symbols are not allowed!")

    else:
        w2 = count_letters(w)
        if w2 == 1:
            print("✅ Your word has only one letter")
        else:
            print(f"✅ Your word has {w2} letters")
        	
        	
def count_vowels(word):
    vowels = "aeiouAEIOU"  
    count = 0
    for letter in word:
        if letter in vowels:
            count += 1
    return count

while True:
    print("----- How many vowels are in a word -----")
    w = str(input("Enter your word: ")).strip()

    # Check if input is empty
    if not w:  
        print("❌ Please enter a word!")

    # Check if input contains only alphabets
    elif not w.isalpha():
        print("❌ Only letters are allowed! No numbers or symbols.")

    else:
        w2 = count_vowels(w)
        if w2 == 1:
            print("✅ Your word has only one vowel")
        elif w2 == 0:
            print("✅ No vowels in your word")
        else:		
            print("✅ Your word has", w2, "vowels")      
       
        	
        	 	
        	 	 	
def count_consonents(word):
    consonents= "bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ"  
    count = 0
    for letter in word:
        if letter in consonents:
            count += 1
    return count
    
while True:
    print("----- How many consonents are in a word -----")
    w = str(input("Enter your word: ")).strip()

    # Check if input is empty
    if not w:  
        print("❌ Please enter a word!")

    # Check if input contains only alphabets
    elif not w.isalpha():
        print("❌ Only letters are allowed! No numbers or symbols.")

    else:
        w2 = count_consonents(w)
        if w2 == 1:
            print("✅ Your word has only one consonent")
        elif w2 == 0:
            print("✅ No consonent in your word")
        else:		
            print("✅ Your word has", w2, "consonents")
      	 	 	 	 	



	
