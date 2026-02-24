from fractions import Fraction as frac
import random


def assert_zawjayn(new):

    if new.get('zawj') == None or new.get('zawja') == None:
        
        if new.get('is_married') == 'Yes' and new.get('sex') == 'Male':
            new['zawja'] = True

        elif new.get('is_married') == 'Yes' and new.get('sex') == 'Female':
            new['zawj'] = True

    return new

def lizakari(n_male, n_female, baqi):

    male_ratio = (n_male * 2) / (n_male*2 + n_female)

    male_baqi = male_ratio * baqi
    female_baqi = baqi - male_baqi

    return male_baqi, female_baqi

def add_zawjayn_to_test(new):

    new['zawj'] = False
    new['zawja'] = False

    if new.get('is_married') == 'Yes' and new.get('sex') == 'Male':
        new['zawja'] = True

    elif new.get('is_married') == 'Yes' and new.get('sex') == 'Female':
        new['zawj'] = True

    return new

def taseeb(total, new, finish, asib):

    baqi = 1.0 - total

    ### SINGLE ASIB ###

    if asib == 'ibn':

        finish['ibn'] += baqi

    elif asib == 'iibn':

        finish['iibn'] += baqi

    elif asib == 'iiibn':

        finish['iiibn'] += baqi
    
    elif asib == 'ibn-bint':

        n_male = new['ibn']
        n_female = new['bint']

        male_baqi, female_baqi = lizakari(n_male, n_female, baqi)

        finish['ibn'] += male_baqi
        finish['bint'] += female_baqi

    elif asib == 'iibn-bibn':

        n_male = new['iibn']
        n_female = new['bibn']

        male_baqi, female_baqi = lizakari(n_male, n_female, baqi)

        finish['iibn'] += male_baqi
        finish['bibn'] += female_baqi

    elif asib == 'iiibn-biibn':

        n_male = new.get('iiibn')
        n_female = new.get('biibn')

        male_baqi, female_baqi = lizakari(n_male, n_female, baqi)

        finish['iiibn'] += male_baqi
        finish['biibn'] += female_baqi


    elif asib == 'iiibn-biibn-bibn':

        n_male = new.get('iiibn')
        n_female1 = new.get('biibn')
        n_female2 = new.get('bibn')
        n_female = n_female1 + n_female2

        male_baqi, female_baqi = lizakari(n_male, n_female, baqi)

        finish['iiibn'] += male_baqi
        finish['biibn'] += (female_baqi / n_female) * n_female1
        finish['bibn'] += (female_baqi / n_female) * n_female2

    elif asib == 'ab':

        finish['ab'] += baqi

    elif asib == 'jadd':

        finish['jadd'] += baqi

    elif asib == 'shaqiq':

        finish['shaqiq'] += baqi

    elif asib == 'shaqiqa':

        finish['shaqiqa'] += baqi


    elif asib == 'shaqiq-shaqiqa':

        n_male = new.get('shaqiq')
        n_female = new.get('shaqiqa')

        male_baqi, female_baqi = lizakari(n_male, n_female, baqi)

        finish['shaqiq'] += male_baqi
        finish['shaqiqa'] += female_baqi

    elif asib == 'aliab':

        finish['aliab'] += baqi
    
    elif asib == 'uliab':

        finish['uliab'] += baqi

    elif asib == 'aliab-uliab':

        n_male = new.get('aliab')
        n_female = new.get('uliab')

        male_baqi, female_baqi = lizakari(n_male, n_female, baqi)

        finish['aliab'] += male_baqi
        finish['uliab'] += female_baqi 

    elif new.get('ibnamm_sh'): 
            asib = 'ibnamm_sh'
            finish['ibnamm_sh'] = 0
            finish['ibnamm_sh'] += baqi
    
    elif new.get('ibnamm_liab'): 
        asib = 'ibnamm_liab' 
        finish['ibnamm_liab'] += baqi           
    
    elif new.get('amm'): 
        asib = 'amm'
        finish['amm'] += baqi
    
    return finish, asib

def awl(total, finish):

    if total > 1.0:

        awl_factor = 1 / total

        finish = {k:v * awl_factor for k,v in finish.items()}
    return finish
            
def furoo(new, finish, asib, has_hawashi):
    
    # AHWAAL AL-BANAAT
    bint_taking_half = False
    bints_taking_twothirds = False
    has_missed_girls = False

    # TA'SEEB IBN WAL BINT

    if new.get('ibn') and not new.get('bint'):
        asib = 'ibn'

    elif new.get('ibn') and new.get('bint'):
        asib = 'ibn-bint'

    # FARD AL BINT 
       
    elif not new.get('ibn') and new.get('bint'):
        if new.get('bint') == 1:

            finish['bint'] = frac(1,2)
            bint_taking_half = True

        else:
            finish['bint'] = frac(2,3)
            bints_taking_twothirds = True


    # GRAND-CHILDREN

    if asib == None and (new.get('iibn') or new.get('bibn')):

        # TA'SEEB IBN-IBN AND BINT-AL-IBN
    
        if new.get('iibn'):
            if not new.get('bibn'):
                asib = 'iibn'
            else:
                asib = 'iibn-bibn'
        
        # TAKMULA BINT IBN

        elif new.get('bibn') and bint_taking_half:
                finish['bibn'] = frac(1,6)
                bints_taking_twothirds = True

        # FARD BINT IBN

        elif new.get('bibn') and not any([bint_taking_half or bints_taking_twothirds]):
            
            if new.get('bibn') == 1:
                finish['bibn'] = frac(1,2)
                bint_taking_half = True
            else:
                finish['bibn'] = frac(2,3)
                bints_taking_twothirds = True

        elif bints_taking_twothirds and new.get('bibn'):
                has_missed_girls = True

    # GREAT GRAND CHILDREN

    if asib == None:
        
        # TA'SEEB AWLAAD IBN IBN

        if new.get('iiibn'):
            
            if not has_missed_girls and not new.get('biibn'):
                asib = 'iiibn'

            elif has_missed_girls and new.get('bibn') and not new.get('biibn'):
                asib = 'iiibn-bibn'
            
            elif not has_missed_girls and new.get('biibn'):
                asib = 'iiibn-biibn'
            
            elif has_missed_girls and new.get('bibn') and new.get('biibn'):
                asib = 'iiibn-biibn-bibn'

        # TAKMULA OF BINT-IBN
        
        elif new.get('biibn') and bint_taking_half and not bints_taking_twothirds:
            finish['biibn'] = frac(1,6)
            bints_taking_twothirds = True

        # FARD BINT IBN IBN
        elif new.get('biibn') and not any([bints_taking_twothirds, bint_taking_half]):
            if new.get('biibn') == 1:
                finish['biibn'] = frac(1,2)
                has_used_half = True
            else:
                finish['biibn'] = frac(2,3)
                has_used_twothirds = True

    return finish, asib, bint_taking_half, bints_taking_twothirds

def usool(new, finish, asib, has_any_furoo, has_m_furoo, has_jame):
    
    if has_any_furoo:

        if new.get('ab'):
            finish['ab'] = frac('1/6')
            if not has_m_furoo:
                asib = 'ab'

        elif new.get('jadd'): 
            finish['jadd'] = frac('1/6')
            if not has_m_furoo:
                asib = 'jadd'           

        if new.get('umm'): 
            finish['umm'] = frac('1/6')

        elif new.get('jadda'): 
            finish['jadda'] = frac('1/6')

    elif not has_any_furoo and not has_jame:
        if new.get('umm'): 
            finish['umm'] = frac('1/3')

        elif new.get('jadda'): 
            finish['jadda'] = frac('1/6')

    elif has_jame: # im not sure about the utility of this block

        if new.get('umm'): 
            finish['umm'] = frac('1/6')

        elif new.get('jadda'): 
            finish['jadda'] = frac('1/6')

    # TASEEB AL ABAA'

    if not has_m_furoo:
        if new.get('ab'):
            asib = 'ab'
        elif new.get('jadd'):
            asib = 'jadd'
                
    return finish, asib

def zawjayn(new, finish, has_any_furoo):
        
    if new.get('zawj') and has_any_furoo:

        finish['zawj'] = frac('1/4')

    elif new.get('zawj') and not has_any_furoo:

        finish['zawj'] = frac('1/2')

    elif new.get('zawja') and has_any_furoo:


        finish['zawja'] = frac('1/8')

    elif new.get('zawja') and not has_any_furoo:

        finish['zawja'] = frac('1/4')
    
    return finish

def kalala(new, finish):

    if new.get('lium'):

        if new.get('lium') == 1:
            finish['lium'] = frac(1/6)
        elif new.get('lium') > 1:
            finish['lium'] = frac(1/3)

    return finish

def hawashi(new, finish, asib, bint_taking_half, bints_taking_twothirds, has_any_furoo, has_m_usool, has_m_furoo, shaqiqa_taking_half, shaqiqas_taking_twothirds):
    
    # TA'SEEB AL-ASHIQQAA'
    
    if new.get('shaqiq') and not new.get('shaqiqa'):
        asib = 'shaqiq'
    
    elif new.get('shaqiq') and new.get('shaqiqa'):
        asib = 'shaqiq-shaqiqa'
    
    # FARD AL-UKHT ASH-SHAQIQA
    
    elif not new.get('shaqiq') and new.get('shaqiqa') and not has_any_furoo:

        if new.get('shaqiqa') and new.get('shaqiqa') == 1:
            finish['shaqiqa'] = frac('1/2')
            shaqiqa_taking_half = True


        elif new.get('shaqiqa') and new.get('shaqiqa') > 1:
            finish['shaqiqa'] = frac('2/3')
            shaqiqas_taking_twothirds = True
 
    # TA'SEEB AL-UKHT ASH-SHAQIQA BIL BINT
    
    elif asib == None and new.get('shaqiqa') and (bint_taking_half or bints_taking_twothirds):
        asib = 'shaqiqa'
        
    # MEERAATH AL-IKHWA LI-ABB'
    
    if asib == None:
        
        if new.get('aliab') and not new.get('uliab'):
            asib = 'aliab'
    
        elif asib == None and new.get('aliab') and new.get('uliab'):
            asib = 'aliab-uliab'

        # TA'SEEB AL-UKHT LI-AB BIL BINT
        elif asib == None  and new.get('uliab') and not new.get('shaqiqa') and (bint_taking_half or bints_taking_twothirds):
            asib = 'uliab'
        
        # FARD AL-UKHT LI-AB
        elif not new.get('aliab'):

            if new.get('uliab') and not has_any_furoo and new.get('shaqiqa') and shaqiqa_taking_half and not any([shaqiqas_taking_twothirds, bints_taking_twothirds, bint_taking_half]): # takmula
                finish['uliab'] = frac('1/6')

            elif new.get('uliab') and not has_any_furoo and not (new.get('shaqiqa') or new.get('shaqiq')):
                if new.get('uliab') == 1:
                    finish['uliab'] = frac('1/2')
                elif new.get('uliab') > 1:
                    finish['uliab'] = frac('2/3')
    
    return finish, asib, shaqiqa_taking_half, shaqiqas_taking_twothirds
        
def radd(total, finish):

    ziyada = 1 - total
    radd_factors = finish.copy()
    radd_factors = {k:v for k,v in radd_factors.items() if k not in ('zawj', 'zawja')}

    if len(radd_factors) > 1:
        temp_total = sum(radd_factors.values())

        if temp_total == 0:
           ending = 'Unallocated baqi'

        else:
            radd_factors = {k:v/temp_total for k,v in radd_factors.items()}

            for k, v in radd_factors.items():
                finish[k] = finish.get(k, 0) + v * ziyada

            ending = 'radd'
    else:
        k, v = next(iter(radd_factors.items()))
        finish[k] = finish.get(k, 0) + v * ziyada
        ending = 'radd'

    return finish, ending

def faraid_simulation(prob_married = 0.5, m_asl = True, m_fare = True, f_fare = True):
    
    if m_fare:
        boys = random.randrange(0,3)
    else:
        boys = 0

    if m_asl:
        dads = random.randrange(0,2)
    else:
        dads = 0

    if f_fare:
        girls = random.randrange(0,3)
    else:
        girls = 0
    
    roll = random.uniform(0,1)
    is_married = 'Yes' if roll < prob_married else 'No'

    new = { 
    'is_married': is_married,
    'sex': random.choice(["Male", "Female"]), 
    'bint': girls, 
    'ibn': boys, 
    'bibn': girls, 
    'iibn': boys, 
    'biibn': girls, 
    'iiibn': boys, 
    'umm': random.randrange(0,2), 
    'jadda': random.randrange(0,1), 
    'ab': dads, 
    'jadd': dads, 
    'has_siblings': random.randrange(0,1), 
    'lium': random.randrange(0,3), 
    'shaqiqa': random.randrange(0,3), 
    'shaqiq': random.randrange(0,3), 
    'uliab': random.randrange(0,3), 
    'aliab': random.randrange(0,3), 
    'ibnamm_sh': random.randrange(0,3), 
    'ibnamm_liab': random.randrange(0,3), 
    'amm': random.randrange(0,3)}
    
    new = add_zawjayn_to_test(new)
    
    new = {k:v for k,v in new.items() if v != 0}
    
    _, finish, ending, asib, final_total, status = calculate(new)
    return new, finish, ending, final_total, asib, status

def calculate(new):

    """
    Returns:
        user_data (dict): Description of user_data value.
        finish (dict): Distribution of assets among heirs.
        ending (str): How the distribution ended: Ta'seeb, 'awl or radd.
        asib (str): Who the 'Aasib is, if present.
        final_total (float): the sum of all the tarikah that has been accoutned for
        status (str): How the overall mas'alah ran (Failed / Complete).
    """
    ### prep ### 
    
    ending = None
    asib = None
    new = assert_zawjayn(new)
    finish = {k: v for k, v in new.items() if v!= 0}
    finish = {k: v if k in ('email', 'fname', 'lname') else 0 for k, v in new.items()}
    
    # GET STATUSES #
    
    is_married = any([new.get('zawj'), new.get('zawja')])
    has_any_usool = any([new.get('ab'), new.get('jadd'), new.get('umm'), new.get('jadda')])
    has_m_usool = any([new.get('ab'), new.get('jadd')])
    has_m_furoo = any([new.get('ibn'), new.get('iibn'), new.get('iiibn')] )
    has_any_furoo = any([new.get('ibn'), new.get('bint'), new.get('iibn'), new.get('bibn'), new.get('iiibn'), new.get('biibn')] )
    has_jame = sum(value for value in [new.get('shaqiq'), new.get('shaqiqa'), new.get('aliab'), new.get('uliab'), new.get('lium')] if value is not None) > 1
    has_hawashi = any([new.get('shaqiq'), new.get('shaqiqa'), new.get('aliab'), new.get('uliab'), new.get('lium'), new.get('amm'), new.get('ibnamm')] )
    bint_taking_half = False
    bints_taking_twothirds = False
    shaqiqa_taking_half = False
    shaqiqa_taking_twothirds = False
    is_kalala = not any([has_any_furoo, has_m_usool])
    asib_present = any([has_m_usool, has_m_furoo, new.get('shaqiq'), new.get('aliab'), new.get('amm'), new.get('ibnamm_sh'), new.get('ibnamm_liab')])
    
    # GET SPECIAL CASES #
    
    is_umuriya1 = all([new.get('ab'), new.get('umm'), new.get('zawj'), not any([has_jame, has_any_furoo])])
    is_umuriya2 = all([new.get('ab'), new.get('umm'), new.get('zawja'), not any([has_jame, has_any_furoo])])
    is_umuriya = any([is_umuriya1, is_umuriya2])
    if new.get('lium'):
        is_mushtaraka = all([new.get('zawj'), (new.get('umm') or new.get('jadda')), new.get('lium') > 1, new.get('shaqiq')]) and not any([has_any_furoo, has_m_usool])
    else: is_mushtaraka = False

    if is_umuriya:
        if is_umuriya1:

            finish['zawj'] = frac('3/6')
            finish['ab'] = frac('2/6')
            finish['umm'] = frac('1/6')
            finish = {k: v for k, v in finish.items() if v!= 0}
            ending = 'umuriya1'

        elif is_umuriya2:

            finish['zawja'] = frac('1/4')
            finish['ab'] = frac('1/2')
            finish['umm'] = frac('1/4')
            ending = 'umuriya2'

    elif is_mushtaraka:
        
        finish['zawj'] = frac('1/2')
        finish['all full siblings and maternal half siblings'] = frac('1/3')
        
        if new.get('umm'):
            finish['umm'] = frac('1/6')
        elif new.get('jadda'):
            finish['jadda'] = frac('1/6')

        ending = 'mushtaraka'       

    else:
        if is_married:
            finish = zawjayn(new, finish, has_any_furoo)

        if has_any_usool:
            finish, asib = usool(new, finish, asib, has_any_furoo,has_m_furoo, has_jame)

        if has_any_furoo:
            finish, asib, bint_taking_half, bints_taking_twothirds = furoo(new, finish, asib, has_hawashi)

        if has_hawashi:
            if not any([has_m_usool, has_m_furoo]):
                finish, asib, shaqiqa_taking_half, shaqiqas_taking_twothirds = hawashi(new, finish, asib, bint_taking_half, bints_taking_twothirds, has_any_furoo, has_m_usool, has_m_furoo, shaqiqa_taking_half, shaqiqa_taking_twothirds)
        if is_kalala:
            finish = kalala(new, finish)

    
    
    ## CLEAN ENDINGS

    user_data = {k: v for k, v in finish.items() if k in ('email', 'fname', 'lname')}
    finish = {k: v for k, v in finish.items() if k not in ('email', 'fname', 'lname')}
    
    total = sum(finish.values())

    if total > 1.0:
        finish = awl(total, finish)
        ending = 'awl'

    if total < 1.0:
        if asib_present or asib: 
            finish, asib = taseeb(total, new, finish, asib)
            ending = 'taseeb'

        elif not asib_present and total > 0:
            finish, ending = radd(total, finish)

    finish = {k: v for k, v in finish.items() if v!= 0}
    finish = {k: round(v, 4) for k,v in finish.items()}

    post_ending_total = sum(finish.values())

    if post_ending_total == 0 and ending == None:
        status = 'Failed'
        ending = 'No valid heirs.'
    elif round(post_ending_total,2) == 1.00:
        status = 'Complete'
    else:
        status = 'Unknown'

    final_total = sum(finish.values())
    
    return user_data, finish, ending, asib, final_total, status