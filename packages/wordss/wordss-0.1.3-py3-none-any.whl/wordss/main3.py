def ccs():
    def count_consonents(word):
        consonents = "bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ"  
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
                print(f"✅ Your word has {w2} consonents")

# 🔹 Call cc() so the program starts
ccs()