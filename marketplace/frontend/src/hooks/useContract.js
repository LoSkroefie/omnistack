import { useMemo } from 'react';
import { useWeb3React } from '@web3-react/core';
import { Contract } from '@ethersproject/contracts';

import OmniStackMarketplace from '../contracts/OmniStackMarketplace.json';

export function useContract(address, ABI) {
    const { library, account } = useWeb3React();

    return useMemo(() => {
        if (!address || !ABI || !library) {
            return null;
        }

        try {
            return new Contract(
                address,
                ABI,
                library.getSigner(account).connectUnchecked()
            );
        } catch (error) {
            console.error('Failed to create contract:', error);
            return null;
        }
    }, [address, ABI, library, account]);
}

export function useMarketplaceContract() {
    return useContract(
        process.env.REACT_APP_MARKETPLACE_ADDRESS,
        OmniStackMarketplace.abi
    );
}
