
/**
 * @description - Extract the account details from the extracted texts
 * @param {String} params 
 * @returns {Array<accountDetails>}
 */
exports.extractAccountDetails = async function (params) {
    const acctNumRegex = /^\d{10}$/
    const splittedTexts = params.split(/\s+/).map(text => text.replace(/[^a-zA-Z0-9]/g, ''))

    let accountDetails = []
    // console.log(splittedTexts)

    splittedTexts.map((item, position) => {
        // Check if the word is an account number
        if (acctNumRegex.test(Number(item))) {
            accountDetails.push(item)
        }
        // Check if the word is a bank string
        else if (item.toLowerCase() === 'bank') {
            accountDetails.push(`${splittedTexts[position - 1]} Bank`)
        }
    })


    return accountDetails
}