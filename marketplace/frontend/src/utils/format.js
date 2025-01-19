import { formatUnits } from '@ethersproject/units';

export function formatEther(value) {
    return formatUnits(value, 18);
}

export function shortenAddress(address, chars = 4) {
    if (!address) return '';
    return `${address.substring(0, chars + 2)}...${address.substring(42 - chars)}`;
}

export function formatModuleMetadata(metadata) {
    try {
        if (typeof metadata === 'string') {
            return JSON.parse(metadata);
        }
        return metadata;
    } catch (error) {
        console.error('Error parsing module metadata:', error);
        return {};
    }
}
