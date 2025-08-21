def cls():
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

# 🔹 Call cl() so it actually runs
cls()