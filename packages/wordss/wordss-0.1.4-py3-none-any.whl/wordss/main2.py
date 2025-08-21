def cvs():
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
                print(f"✅ Your word has {w2} vowels")

# 🔹 Call cv() so the program starts
cvs()
